from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.ml.recommender import ShoppingRecommender

router = APIRouter(prefix="/products", tags=["recommendations"])

_recommender = ShoppingRecommender()


@router.get("/{product_id}/recommendation", response_model=Dict[str, Any])
def get_recommendation(product_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    recommendation = _recommender.should_buy_now(product_id, db)
    recommendation["product_id"] = product_id
    recommendation["product_name"] = product.name
    return recommendation
