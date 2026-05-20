from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.price import PriceHistory
from app.schemas.price import PriceHistoryRead

router = APIRouter(prefix="/products", tags=["prices"])


@router.get("/{product_id}/prices", response_model=List[PriceHistoryRead])
def get_price_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> List[PriceHistoryRead]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    since = datetime.utcnow() - timedelta(days=days)
    prices = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.product_id == product_id,
            PriceHistory.scraped_at >= since,
        )
        .order_by(PriceHistory.scraped_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return prices


@router.get("/{product_id}/prices/stats", response_model=Dict[str, Any])
def get_price_stats(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    since = datetime.utcnow() - timedelta(days=days)
    result = (
        db.query(
            func.min(PriceHistory.price).label("min_price"),
            func.max(PriceHistory.price).label("max_price"),
            func.avg(PriceHistory.price).label("avg_price"),
            func.count(PriceHistory.id).label("count"),
        )
        .filter(
            PriceHistory.product_id == product_id,
            PriceHistory.scraped_at >= since,
        )
        .first()
    )

    # Get latest price
    latest = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.scraped_at.desc())
        .limit(1)
        .first()
    )

    return {
        "product_id": product_id,
        "days": days,
        "min_price": float(result.min_price) if result.min_price else None,
        "max_price": float(result.max_price) if result.max_price else None,
        "avg_price": round(float(result.avg_price), 2) if result.avg_price else None,
        "current_price": float(latest.price) if latest else None,
        "count": result.count,
    }
