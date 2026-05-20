from datetime import datetime
from pydantic import BaseModel, EmailStr


class AlertCreate(BaseModel):
    product_id: int
    user_email: str
    threshold_price: float


class AlertRead(BaseModel):
    id: int
    product_id: int
    user_email: str
    threshold_price: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
