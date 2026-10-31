from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.forecast_demand import ForecastDemand

class DemandService:
    def __init__(self, db: Session):
        self.db = db

    def get_demands(
        self,
        sku_id: Optional[str] = None,
        location_id: Optional[str] = None,
        iso_week: Optional[str] = None,
        demand_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ForecastDemand]:
        query = self.db.query(ForecastDemand)
        if sku_id:
            query = query.filter(ForecastDemand.sku_id == sku_id)
        if location_id:
            query = query.filter(ForecastDemand.location_id == location_id)
        if iso_week:
            query = query.filter(ForecastDemand.iso_week == iso_week)
        if demand_type:
            query = query.filter(ForecastDemand.demand_type == demand_type)
        return query.offset(skip).limit(limit).all()

    def get_demand_by_id(self, demand_id: str) -> Optional[ForecastDemand]:
        return self.db.query(ForecastDemand).filter(ForecastDemand.demand_id == demand_id).first()
