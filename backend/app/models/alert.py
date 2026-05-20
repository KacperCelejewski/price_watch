from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    user_email: Mapped[str] = mapped_column(String(320), nullable=False)
    threshold_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    product: Mapped["Product"] = relationship("Product", back_populates="alerts")
