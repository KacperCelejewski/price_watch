from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.scrapers.scheduler import scrape_product

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.post("/trigger/{product_id}", response_model=Dict[str, Any])
def trigger_scrape(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Run scrape synchronously for immediate feedback
    price = scrape_product(product, db)

    return {
        "product_id": product_id,
        "product_name": product.name,
        "scraped_price": price,
        "status": "success" if price is not None else "no_price_found",
    }
