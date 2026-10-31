from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.production_plan import ProductionPlan, ProductionCapacity, BOMHeader, BOMComponent

class ProductionService:
    def __init__(self, db: Session):
        self.db = db

    def get_production_plans(
        self,
        sku_id: Optional[str] = None,
        location_id: Optional[str] = None,
        iso_week: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductionPlan]:
        query = self.db.query(ProductionPlan)
        if sku_id:
            query = query.filter(ProductionPlan.sku_id == sku_id)
        if location_id:
            query = query.filter(ProductionPlan.location_id == location_id)
        if iso_week:
            query = query.filter(ProductionPlan.iso_week == iso_week)
        if status:
            query = query.filter(ProductionPlan.status == status)
        return query.offset(skip).limit(limit).all()

    def get_bom_for_sku(self, finished_sku_id: str) -> Optional[BOMHeader]:
        return self.db.query(BOMHeader).filter(
            BOMHeader.finished_sku_id == finished_sku_id,
            BOMHeader.is_active == True
        ).first()

    def get_capacities(self, location_id: Optional[str] = None, iso_week: Optional[str] = None) -> List[ProductionCapacity]:
        query = self.db.query(ProductionCapacity)
        if location_id:
            query = query.filter(ProductionCapacity.location_id == location_id)
        if iso_week:
            query = query.filter(ProductionCapacity.iso_week == iso_week)
        return query.all()
