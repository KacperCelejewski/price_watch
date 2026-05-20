from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


class UserSettingsUpdate(BaseModel):
    email: Optional[str] = None
    scrape_interval_hours: Optional[int] = None
    notify_on_drop: Optional[bool] = None
    notify_on_anomaly: Optional[bool] = None
    notify_on_recommendation: Optional[bool] = None
    dark_mode: Optional[bool] = None


@router.patch("/settings", response_model=Dict[str, Any])
def update_user_settings(
    payload: UserSettingsUpdate,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Update settings for the first user in the system (single-user mode).
    In a multi-user setup this endpoint would require authentication.
    """
    user = db.query(User).first()
    if not user:
        # Create a default user record if none exists
        user = User(
            email=payload.email or "default@pricewatch.local",
            hashed_password="",
            settings={},
        )
        db.add(user)

    current_settings: Dict[str, Any] = dict(user.settings) if user.settings else {}
    updates = payload.model_dump(exclude_none=True)
    current_settings.update(updates)
    user.settings = current_settings

    db.commit()
    db.refresh(user)

    return {
        "user_id": user.id,
        "settings": user.settings,
    }
