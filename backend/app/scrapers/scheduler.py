from urllib.parse import urlparse
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import SessionLocal
from app.models.product import Product
from app.models.price import PriceHistory
from app.models.scraper_log import ScraperLog, ScraperStatus
from app.scrapers.ceneo import CeneoScraper
from app.scrapers.allegro import AllegroScraper
from app.scrapers.generic import GenericScraper

scheduler = BackgroundScheduler()


def get_scraper_for_url(url: str):
    """Return the appropriate scraper based on URL domain."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if "ceneo.pl" in domain:
        return CeneoScraper()
    elif "allegro.pl" in domain:
        return AllegroScraper()
    else:
        return GenericScraper()


def _write_scraper_log(
    db: Session, product_id: int, status: ScraperStatus, message: str
) -> None:
    try:
        log = ScraperLog(
            product_id=product_id,
            status=status,
            message=message,
            scraped_at=datetime.utcnow(),
        )
        db.add(log)
        db.commit()
    except Exception as exc:
        logger.warning(f"Could not write scraper log: {exc}")
        db.rollback()


def scrape_product(product: Product, db: Session) -> Optional[float]:
    """Scrape price for a single product and save to PriceHistory."""
    scraper = get_scraper_for_url(product.url)
    try:
        price = scraper.scrape(product.url)
        if price is not None:
            record = PriceHistory(
                product_id=product.id,
                price=price,
                currency="PLN",
                scraped_at=datetime.utcnow(),
            )
            db.add(record)
            db.commit()
            logger.info(f"Scraped price {price} PLN for product {product.id} ({product.name})")
            _write_scraper_log(
                db, product.id, ScraperStatus.success, f"Scraped price: {price} PLN"
            )
            return price
        else:
            msg = f"No price found on {product.url}"
            logger.warning(f"No price found for product {product.id} ({product.name})")
            _write_scraper_log(db, product.id, ScraperStatus.error, msg)
            return None
    except Exception as exc:
        msg = str(exc)
        logger.error(f"Error scraping product {product.id}: {exc}")
        db.rollback()
        _write_scraper_log(db, product.id, ScraperStatus.error, msg)
        return None
    finally:
        scraper.close()


def scrape_all_products() -> None:
    """Job: scrape prices for all active products."""
    logger.info("Starting scheduled scrape of all products")
    db: Session = SessionLocal()
    try:
        products = db.query(Product).all()
        logger.info(f"Scraping {len(products)} products")
        for product in products:
            scrape_product(product, db)
    except Exception as exc:
        logger.error(f"Error in scrape_all_products: {exc}")
    finally:
        db.close()
    logger.info("Scheduled scrape completed")


def start_scheduler() -> None:
    """Start the APScheduler background scheduler."""
    from apscheduler.triggers.cron import CronTrigger
    from app.ml.training import retrain_all_models_job

    scheduler.add_job(
        scrape_all_products,
        trigger=IntervalTrigger(hours=settings.scraper_interval_hours),
        id="scrape_all_products",
        name="Scrape all product prices",
        replace_existing=True,
    )

    # Retrain all ML models every day at 3 AM
    scheduler.add_job(
        retrain_all_models_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="retrain_all_models",
        name="Retrain price prediction models",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        f"Scheduler started — scraping every {settings.scraper_interval_hours} hours, "
        "retraining models daily at 03:00"
    )


def stop_scheduler() -> None:
    """Stop the scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
