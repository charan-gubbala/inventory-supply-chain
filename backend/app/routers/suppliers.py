from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.schemas.schemas import SupplierRead, SupplierCapacityRead, LeadTimeRead

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.get("", response_model=List[SupplierRead])
def list_suppliers(
    status: Optional[str] = None,
    min_rating: Optional[float] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Supplier)
    if status:
        query = query.filter(Supplier.status == status)
    if min_rating:
        query = query.filter(Supplier.rating >= min_rating)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%") | Supplier.supplier_id.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()

@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    sup = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not sup:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return sup

@router.get("/{supplier_id}/capacities", response_model=List[SupplierCapacityRead])
def get_supplier_capacities(supplier_id: str, db: Session = Depends(get_db)):
    return db.query(SupplierCapacity).filter(SupplierCapacity.supplier_id == supplier_id).all()

@router.get("/{supplier_id}/lead-times", response_model=List[LeadTimeRead])
def get_supplier_lead_times(supplier_id: str, db: Session = Depends(get_db)):
    return db.query(LeadTime).filter(LeadTime.supplier_id == supplier_id).all()
