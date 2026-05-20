from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.price import PriceHistory
from app.ml.data_processing import clean_price_series
from app.ml.anomaly import AnomalyDetector

router = APIRouter(prefix="/products", tags=["anomalies"])

_detector = AnomalyDetector()


@router.get("/{product_id}/anomalies", response_model=List[Dict[str, Any]])
def get_anomalies(
    product_id: int,
    days: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    from datetime import datetime, timedelta
    since = datetime.utcnow() - timedelta(days=days)

    prices = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.product_id == product_id,
            PriceHistory.scraped_at >= since,
        )
        .order_by(PriceHistory.scraped_at.asc())
        .all()
    )

    if len(prices) < 4:
        return []

    df = clean_price_series(prices)
    if df.empty or "price" not in df.columns:
        return []

    price_series = df.set_index("date")["price"] if "date" in df.columns else df["price"]
    return _detector.detect(price_series)
