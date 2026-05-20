from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, model_config
from app.schemas.price import PriceHistoryRead


class ProductCreate(BaseModel):
    name: str
    url: str
    shop: Optional[str] = None
    category: Optional[str] = None


class ProductRead(BaseModel):
    id: int
    name: str
    url: str
    shop: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime

    model_config = model_config = {"from_attributes": True}


class ProductWithPrices(ProductRead):
    prices: List[PriceHistoryRead] = []
