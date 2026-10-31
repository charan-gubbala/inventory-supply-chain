from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.sku import SKU, SKUSubstitute
from backend.app.schemas.schemas import SKURead, SKUCreate, SKUSubstituteRead

router = APIRouter(prefix="/skus", tags=["SKUs"])

@router.get("", response_model=List[SKURead])
def list_skus(
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(SKU)
    if category:
        query = query.filter(SKU.category == category)
    if status:
        query = query.filter(SKU.status == status)
    if search:
        query = query.filter(SKU.name.ilike(f"%{search}%") | SKU.sku_id.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{sku_id}", response_model=SKURead)
def get_sku(sku_id: str, db: Session = Depends(get_db)):
    sku = db.query(SKU).filter(SKU.sku_id == sku_id).first()
    if not sku:
        raise HTTPException(status_code=404, detail="SKU not found")
    return sku

@router.get("/{sku_id}/substitutes", response_model=List[SKUSubstituteRead])
def get_sku_substitutes(sku_id: str, db: Session = Depends(get_db)):
    subs = db.query(SKUSubstitute).filter(SKUSubstitute.original_sku_id == sku_id).all()
    return subs

@router.post("", response_model=SKURead, status_code=201)
def create_sku(sku_in: SKUCreate, db: Session = Depends(get_db)):
    existing = db.query(SKU).filter(SKU.sku_id == sku_in.sku_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="SKU ID already exists")
    sku = SKU(**sku_in.dict())
    db.add(sku)
    db.commit()
    db.refresh(sku)
    return sku
