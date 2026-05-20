from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, DateTime, Numeric, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.product import Product


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="PLN", nullable=False)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    product: Mapped["Product"] = relationship("Product", back_populates="prices")

    __table_args__ = (
        Index("ix_price_product_scraped", "product_id", "scraped_at"),
    )
