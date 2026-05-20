from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.product import Product
from app.schemas.alert import AlertCreate, AlertRead

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertRead, status_code=201)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)) -> AlertRead:
    product = db.query(Product).filter(Product.id == alert.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("", response_model=List[AlertRead])
def list_alerts(
    product_id: int = Query(None, description="Filter by product ID"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
) -> List[AlertRead]:
    query = db.query(Alert)
    if product_id is not None:
        query = query.filter(Alert.product_id == product_id)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    return query.all()


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db)) -> None:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    db.delete(alert)
    db.commit()
