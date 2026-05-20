from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductWithPrices

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=List[ProductRead])
def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (partial match)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> List[ProductRead]:
    query = db.query(Product)
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=ProductRead, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> ProductRead:
    existing = db.query(Product).filter(Product.url == product.url).first()
    if existing:
        raise HTTPException(status_code=409, detail="Product with this URL already exists")
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/{product_id}", response_model=ProductWithPrices)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductWithPrices:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
