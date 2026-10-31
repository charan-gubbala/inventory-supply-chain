from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.app.database import get_db
from backend.app.models.production_plan import ProductionPlan, BOMHeader, BOMComponent
from backend.app.schemas.schemas import ProductionPlanRead, ProductionPlanCreate

router = APIRouter(prefix="/production-plans", tags=["Production Planning"])

@router.get("", response_model=List[ProductionPlanRead])
def list_production_plans(
    sku_id: Optional[str] = None,
    location_id: Optional[str] = None,
    iso_week: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ProductionPlan)
    if sku_id:
        query = query.filter(ProductionPlan.sku_id == sku_id)
    if location_id:
        query = query.filter(ProductionPlan.location_id == location_id)
    if iso_week:
        query = query.filter(ProductionPlan.iso_week == iso_week)
    if status:
        query = query.filter(ProductionPlan.status == status)
    return query.offset(skip).limit(limit).all()

@router.post("", response_model=ProductionPlanRead, status_code=201)
def create_production_plan(plan_in: ProductionPlanCreate, db: Session = Depends(get_db)):
    count = db.query(ProductionPlan).count() + 1
    year = plan_in.start_date.year
    plan_id = f"PROD-{year}-{count:06d}"

    plan = ProductionPlan(
        plan_id=plan_id,
        sku_id=plan_in.sku_id,
        location_id=plan_in.location_id,
        iso_week=plan_in.iso_week,
        planned_quantity=plan_in.planned_quantity,
        produced_quantity=0,
        status="PLANNED",
        start_date=plan_in.start_date,
        end_date=plan_in.end_date
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
