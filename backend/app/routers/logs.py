from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.scraper_log import ScraperLog, ScraperStatus

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=List[Dict[str, Any]])
def get_logs(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    status: Optional[ScraperStatus] = Query(None, description="Filter by status: success|error"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    query = db.query(ScraperLog)
    if product_id is not None:
        query = query.filter(ScraperLog.product_id == product_id)
    if status is not None:
        query = query.filter(ScraperLog.status == status)
    logs = query.order_by(ScraperLog.scraped_at.desc()).limit(limit).all()
    return [
        {
            "id": log.id,
            "product_id": log.product_id,
            "status": log.status.value,
            "message": log.message,
            "scraped_at": log.scraped_at.isoformat(),
        }
        for log in logs
    ]
