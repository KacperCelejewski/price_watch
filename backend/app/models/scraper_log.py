from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
import enum


class ScraperStatus(str, enum.Enum):
    success = "success"
    error = "error"


class ScraperLog(Base):
    __tablename__ = "scraper_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ScraperStatus] = mapped_column(
        SAEnum(ScraperStatus, name="scraper_status"), nullable=False
    )
    message: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
