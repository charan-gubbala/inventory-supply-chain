from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime

class SupplierService:
    def __init__(self, db: Session):
        self.db = db

    def get_suppliers(
        self,
        status: Optional[str] = None,
        min_rating: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Supplier]:
        query = self.db.query(Supplier)
        if status:
            query = query.filter(Supplier.status == status)
        if min_rating:
            query = query.filter(Supplier.rating >= min_rating)
        return query.offset(skip).limit(limit).all()

    def get_supplier_by_id(self, supplier_id: str) -> Optional[Supplier]:
        return self.db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    def get_capacities(self, supplier_id: Optional[str] = None, sku_id: Optional[str] = None) -> List[SupplierCapacity]:
        query = self.db.query(SupplierCapacity)
        if supplier_id:
            query = query.filter(SupplierCapacity.supplier_id == supplier_id)
        if sku_id:
            query = query.filter(SupplierCapacity.sku_id == sku_id)
        return query.all()

    def get_lead_times(self, supplier_id: Optional[str] = None, sku_id: Optional[str] = None, location_id: Optional[str] = None) -> List[LeadTime]:
        query = self.db.query(LeadTime)
        if supplier_id:
            query = query.filter(LeadTime.supplier_id == supplier_id)
        if sku_id:
            query = query.filter(LeadTime.sku_id == sku_id)
        if location_id:
            query = query.filter(LeadTime.location_id == location_id)
        return query.all()
