from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.price import PriceHistory
from app.ml.data_processing import clean_price_series
from app.ml.predictor import PricePredictor

router = APIRouter(prefix="/products", tags=["predictions"])


@router.get("/{product_id}/predict", response_model=Dict[str, Any])
def predict_prices(
    product_id: int,
    days: int = Query(7, ge=1, le=90, description="Number of days to predict"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.asc())
        .all()
    )

    if len(prices) < 2:
        raise HTTPException(
            status_code=422,
            detail="Not enough price history to generate predictions (minimum 2 data points required)",
        )

    df = clean_price_series(prices)
    if df.empty:
        raise HTTPException(status_code=422, detail="No clean price data available")

    price_series = df.set_index("date")["price"] if "date" in df.columns else df["price"]

    predictor = PricePredictor()
    predictor.fit(price_series)
    predictions = predictor.predict(days)

    # Save model for reuse
    try:
        predictor.save_model(PricePredictor.model_path(product_id))
    except Exception:
        pass

    # Build forecast dates starting from tomorrow
    start_date = datetime.utcnow().date() + timedelta(days=1)
    forecast = [
        {"date": str(start_date + timedelta(days=i)), "predicted_price": predictions[i]}
        for i in range(len(predictions))
    ]

    return {
        "product_id": product_id,
        "product_name": product.name,
        "days": days,
        "forecast": forecast,
        "current_price": float(prices[-1].price),
        "training_samples": len(df),
    }
