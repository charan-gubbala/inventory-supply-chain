from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from backend.app.database import get_db
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.inventory import Inventory
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.shortage import Shortage
from backend.app.models.mitigation_option import MitigationOption
from backend.app.models.purchase_order import PurchaseOrder
from backend.app.schemas.schemas import (
    DashboardSummary, InventoryTrendPoint, ShortageTrendPoint, SupplierPerformanceItem
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes real-time executive dashboard KPIs from source database tables.
    """
    total_skus = db.query(SKU).count()
    total_locations = db.query(Location).count()
    total_suppliers = db.query(Supplier).count()
    
    total_inventory = db.query(func.sum(Inventory.available_stock)).scalar() or 0
    total_demand = db.query(func.sum(ForecastDemand.forecast_quantity)).scalar() or 0
    
    total_shortages = db.query(Shortage).count()
    critical_shortages = db.query(Shortage).filter(Shortage.severity == "CRITICAL").count()
    
    pending_pos = db.query(PurchaseOrder).filter(PurchaseOrder.status.in_(["CREATED", "APPROVED", "SHIPPED"])).count()
    
    # Supplier capacity utilization
    total_max_cap = db.query(func.sum(SupplierCapacity.max_capacity_per_week)).scalar() or 1
    total_alloc_cap = db.query(func.sum(SupplierCapacity.allocated_capacity)).scalar() or 0
    utilization_pct = round((total_alloc_cap / max(1, total_max_cap)) * 100, 2)

    # Mitigation success rate
    total_mitigations = db.query(MitigationOption).count()
    approved_mitigations = db.query(MitigationOption).filter(MitigationOption.approval_status == "APPROVED").count()
    mitigation_rate = round((approved_mitigations / max(1, total_mitigations)) * 100, 2) if total_mitigations else 0.0

    return DashboardSummary(
        total_skus=total_skus,
        total_locations=total_locations,
        total_suppliers=total_suppliers,
        total_inventory=int(total_inventory),
        total_forecast_demand=int(total_demand),
        total_shortages=total_shortages,
        critical_shortages=critical_shortages,
        pending_purchase_orders=pending_pos,
        supplier_capacity_utilization_pct=utilization_pct,
        mitigation_success_rate_pct=mitigation_rate
    )

@router.get("/inventory-trend", response_model=List[InventoryTrendPoint])
def get_inventory_trend(db: Session = Depends(get_db)):
    """
    Returns weekly aggregated demand vs inventory balances.
    """
    weeks = [w[0] for w in db.query(ForecastDemand.iso_week).distinct().order_by(ForecastDemand.iso_week).all()]
    points = []

    for w in weeks:
        dem_sum = db.query(func.sum(ForecastDemand.forecast_quantity)).filter(ForecastDemand.iso_week == w).scalar() or 0
        inv_sum = db.query(func.sum(Inventory.available_stock)).filter(Inventory.iso_week == w).scalar() or 0
        pab_sum = db.query(func.sum(Inventory.projected_available_balance)).filter(Inventory.iso_week == w).scalar() or 0
        points.append(InventoryTrendPoint(
            iso_week=w,
            total_demand=int(dem_sum),
            total_inventory=int(inv_sum),
            projected_balance=int(pab_sum)
        ))

    return points

@router.get("/shortage-trend", response_model=List[ShortageTrendPoint])
def get_shortage_trend(db: Session = Depends(get_db)):
    """
    Returns weekly shortage count and deficit volume.
    """
    weeks = [w[0] for w in db.query(Shortage.iso_week).distinct().order_by(Shortage.iso_week).all()]
    points = []

    for w in weeks:
        count = db.query(Shortage).filter(Shortage.iso_week == w).count()
        total_qty = db.query(func.sum(Shortage.shortage_quantity)).filter(Shortage.iso_week == w).scalar() or 0
        crit_count = db.query(Shortage).filter(Shortage.iso_week == w, Shortage.severity == "CRITICAL").count()
        points.append(ShortageTrendPoint(
            iso_week=w,
            shortage_count=count,
            total_shortage_quantity=int(total_qty),
            critical_count=crit_count
        ))

    return points

@router.get("/supplier-performance", response_model=List[SupplierPerformanceItem])
def get_supplier_performance(db: Session = Depends(get_db)):
    """
    Returns top supplier ratings, on-time delivery rates, and capacity metrics.
    """
    suppliers = db.query(Supplier).limit(10).all()
    results = []

    for sup in suppliers:
        max_c = db.query(func.sum(SupplierCapacity.max_capacity_per_week)).filter(SupplierCapacity.supplier_id == sup.supplier_id).scalar() or 1
        alloc_c = db.query(func.sum(SupplierCapacity.allocated_capacity)).filter(SupplierCapacity.supplier_id == sup.supplier_id).scalar() or 0
        util = round((alloc_c / max(1, max_c)) * 100, 2)
        results.append(SupplierPerformanceItem(
            supplier_id=sup.supplier_id,
            supplier_name=sup.name,
            rating=float(sup.rating),
            on_time_delivery_rate=float(sup.on_time_delivery_rate),
            allocated_capacity=int(alloc_c),
            max_capacity=int(max_c),
            utilization_pct=util
        ))

    return results
