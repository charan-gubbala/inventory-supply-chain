from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.schemas.schemas import DemandRead

router = APIRouter(prefix="/demand", tags=["Forecast Demand"])

@router.get("", response_model=List[DemandRead])
def list_demand(
    sku_id: Optional[str] = None,
    location_id: Optional[str] = None,
    iso_week: Optional[str] = None,
    demand_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(ForecastDemand)
    if sku_id:
        query = query.filter(ForecastDemand.sku_id == sku_id)
    if location_id:
        query = query.filter(ForecastDemand.location_id == location_id)
    if iso_week:
        query = query.filter(ForecastDemand.iso_week == iso_week)
    if demand_type:
        query = query.filter(ForecastDemand.demand_type == demand_type)
    return query.offset(skip).limit(limit).all()

@router.get("/{demand_id}", response_model=DemandRead)
def get_demand(demand_id: str, db: Session = Depends(get_db)):
    rec = db.query(ForecastDemand).filter(ForecastDemand.demand_id == demand_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Demand record not found")
    return rec
