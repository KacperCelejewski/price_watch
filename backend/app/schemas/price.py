from datetime import datetime
from pydantic import BaseModel


class PriceHistoryRead(BaseModel):
    id: int
    product_id: int
    price: float
    currency: str
    scraped_at: datetime

    model_config = {"from_attributes": True}
