from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.location import Location
from backend.app.schemas.schemas import LocationRead

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("", response_model=List[LocationRead])
def list_locations(
    type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Location)
    if type:
        query = query.filter(Location.type == type)
    if status:
        query = query.filter(Location.status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{location_id}", response_model=LocationRead)
def get_location(location_id: str, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.location_id == location_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc
