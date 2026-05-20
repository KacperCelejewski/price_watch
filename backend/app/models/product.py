from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.price import PriceHistory
    from app.models.alert import Alert


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    shop: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    prices: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory", back_populates="product", cascade="all, delete-orphan"
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", back_populates="product", cascade="all, delete-orphan"
    )
