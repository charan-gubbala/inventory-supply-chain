from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.inventory import Inventory
from backend.app.schemas.schemas import InventoryRead

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryRead])
def list_inventory(
    sku_id: Optional[str] = None,
    location_id: Optional[str] = None,
    iso_week: Optional[str] = None,
    shortage_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(Inventory)
    if sku_id:
        query = query.filter(Inventory.sku_id == sku_id)
    if location_id:
        query = query.filter(Inventory.location_id == location_id)
    if iso_week:
        query = query.filter(Inventory.iso_week == iso_week)
    if shortage_only:
        query = query.filter(Inventory.projected_available_balance < 0)
    return query.offset(skip).limit(limit).all()

@router.get("/{sku_id}/{location_id}", response_model=List[InventoryRead])
def get_inventory_for_lane(sku_id: str, location_id: str, db: Session = Depends(get_db)):
    records = db.query(Inventory).filter(
        Inventory.sku_id == sku_id,
        Inventory.location_id == location_id
    ).order_by(Inventory.iso_week).all()
    if not records:
        raise HTTPException(status_code=404, detail="No inventory balances found for this lane")
    return records
