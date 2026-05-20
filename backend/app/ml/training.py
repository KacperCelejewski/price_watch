from datetime import datetime
from typing import Dict, Any
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import SessionLocal
from app.models.product import Product
from app.models.price import PriceHistory
from app.models.scraper_log import ScraperLog, ScraperStatus
from app.ml.data_processing import clean_price_series
from app.ml.predictor import PricePredictor

MIN_RECORDS_FOR_TRAINING = 30


def retrain_product_model(product: Product, db: Session) -> Dict[str, Any]:
    """
    Retrain the PricePredictor for a single product.

    Returns a summary dict with product_id, status, and error (if any).
    """
    try:
        prices = (
            db.query(PriceHistory)
            .filter(PriceHistory.product_id == product.id)
            .order_by(PriceHistory.scraped_at.asc())
            .all()
        )

        if len(prices) < MIN_RECORDS_FOR_TRAINING:
            logger.debug(
                f"Skipping model retraining for product {product.id}: "
                f"only {len(prices)} records (need {MIN_RECORDS_FOR_TRAINING})"
            )
            return {"product_id": product.id, "status": "skipped", "reason": "insufficient_data"}

        df = clean_price_series(prices)
        if df.empty or "price" not in df.columns:
            return {"product_id": product.id, "status": "skipped", "reason": "no_clean_data"}

        price_series = (
            df.set_index("date")["price"] if "date" in df.columns else df["price"]
        )

        predictor = PricePredictor()
        predictor.fit(price_series)
        model_path = PricePredictor.model_path(product.id)
        predictor.save_model(model_path)

        logger.info(
            f"Retrained model for product {product.id} ({product.name}) "
            f"with {len(df)} clean data points"
        )
        return {"product_id": product.id, "status": "success", "samples": len(df)}

    except Exception as exc:
        logger.error(f"Failed to retrain model for product {product.id}: {exc}")
        return {"product_id": product.id, "status": "error", "error": str(exc)}


def retrain_all_models(db: Session) -> None:
    """
    Iterate all products that have >= MIN_RECORDS_FOR_TRAINING price records,
    retrain their PricePredictor, and log the results.
    """
    logger.info("Starting scheduled model retraining")
    start = datetime.utcnow()

    # Find products with enough records in a single query
    from sqlalchemy import select

    subq = (
        select(PriceHistory.product_id, func.count(PriceHistory.id).label("cnt"))
        .group_by(PriceHistory.product_id)
        .having(func.count(PriceHistory.id) >= MIN_RECORDS_FOR_TRAINING)
        .subquery()
    )
    eligible_products = (
        db.query(Product)
        .join(subq, Product.id == subq.c.product_id)
        .all()
    )

    logger.info(f"Retraining models for {len(eligible_products)} eligible products")
    results = [retrain_product_model(p, db) for p in eligible_products]

    success_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")
    elapsed = (datetime.utcnow() - start).total_seconds()

    logger.info(
        f"Model retraining complete in {elapsed:.1f}s — "
        f"{success_count} success, {error_count} errors, "
        f"{len(results) - success_count - error_count} skipped"
    )


def retrain_all_models_job() -> None:
    """Wrapper for APScheduler: creates its own DB session."""
    db: Session = SessionLocal()
    try:
        retrain_all_models(db)
    finally:
        db.close()
