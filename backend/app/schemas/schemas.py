from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# ----------------- SKU Schemas -----------------
class SKUBase(BaseModel):
    sku_id: str
    name: str
    category: str
    unit_of_measure: str = "UNITS"
    cost_per_unit: float
    price_per_unit: float
    safety_stock_quantity: int = 50
    status: str = "ACTIVE"

class SKUCreate(SKUBase):
    pass

class SKUSubstituteRead(BaseModel):
    substitute_id: str
    original_sku_id: str
    substitute_sku_id: str
    approval_status: str
    conversion_rate: float
    effective_from: date
    effective_to: date

    class Config:
        from_attributes = True

class SKURead(SKUBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- Location Schemas -----------------
class LocationBase(BaseModel):
    location_id: str
    name: str
    type: str
    capacity_units: int
    address: Optional[str] = None
    status: str = "ACTIVE"

class LocationRead(LocationBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ----------------- Forecast Demand Schemas -----------------
class DemandRead(BaseModel):
    demand_id: str
    sku_id: str
    location_id: str
    iso_week: str
    forecast_quantity: int
    demand_type: str
    forecast_date: date
    confidence_level: float

    class Config:
        from_attributes = True

# ----------------- Inventory Schemas -----------------
class InventoryRead(BaseModel):
    inventory_id: str
    sku_id: str
    location_id: str
    iso_week: str
    opening_stock: int
    received_stock: int
    reserved_stock: int
    available_stock: int
    incoming_stock: int
    adjustments: int
    closing_stock: int
    projected_available_balance: int
    unit_of_measure: str

    class Config:
        from_attributes = True

# ----------------- Supplier Schemas -----------------
class SupplierCapacityRead(BaseModel):
    capacity_id: str
    supplier_id: str
    sku_id: str
    max_capacity_per_week: int
    allocated_capacity: int
    available_capacity: int
    effective_from: date
    effective_to: date

    class Config:
        from_attributes = True

class LeadTimeRead(BaseModel):
    lead_time_id: str
    supplier_id: str
    sku_id: str
    location_id: str
    base_lead_time_days: int
    min_order_quantity: int
    cost_per_unit: float

    class Config:
        from_attributes = True

class SupplierRead(BaseModel):
    supplier_id: str
    name: str
    rating: float
    on_time_delivery_rate: float
    status: str
    contact_email: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

# ----------------- Purchase Order Schemas -----------------
class PurchaseOrderCreate(BaseModel):
    supplier_id: str
    sku_id: str
    location_id: str
    order_quantity: int
    unit_cost: float
    order_date: date
    expected_delivery_date: date

class PurchaseOrderUpdateStatus(BaseModel):
    status: str

class PurchaseOrderRead(BaseModel):
    po_id: str
    supplier_id: str
    sku_id: str
    location_id: str
    order_quantity: int
    unit_cost: float
    total_amount: float
    order_date: date
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    status: str

    class Config:
        from_attributes = True

# ----------------- Production Plan Schemas -----------------
class ProductionPlanCreate(BaseModel):
    sku_id: str
    location_id: str
    iso_week: str
    planned_quantity: int
    start_date: date
    end_date: date

class ProductionPlanRead(BaseModel):
    plan_id: str
    sku_id: str
    location_id: str
    iso_week: str
    planned_quantity: int
    produced_quantity: int
    status: str
    start_date: date
    end_date: date

    class Config:
        from_attributes = True

# ----------------- Shortage & Mitigation Schemas -----------------
class ShortageRead(BaseModel):
    shortage_id: str
    sku_id: str
    location_id: str
    iso_week: str
    shortage_quantity: int
    expected_shortage_date: date
    root_cause: str
    severity: str
    detection_date: datetime
    status: str

    class Config:
        from_attributes = True

class MitigationOptionRead(BaseModel):
    mitigation_id: str
    shortage_id: str
    strategy_type: str
    proposed_quantity: int
    estimated_cost: float
    expected_arrival_date: date
    source_supplier_id: Optional[str] = None
    source_location_id: Optional[str] = None
    substitute_sku_id: Optional[str] = None
    capacity_available: bool
    is_feasible: bool
    customer_service_impact: str
    risk_level: str
    recommendation_score: float
    rank: int
    approval_status: str
    rejection_reason: Optional[str] = None
    explanation: str

    class Config:
        from_attributes = True

# ----------------- Dashboard & Metrics Schemas -----------------
class DashboardSummary(BaseModel):
    total_skus: int
    total_locations: int
    total_suppliers: int
    total_inventory: int
    total_forecast_demand: int
    total_shortages: int
    critical_shortages: int
    pending_purchase_orders: int
    supplier_capacity_utilization_pct: float
    mitigation_success_rate_pct: float

class InventoryTrendPoint(BaseModel):
    iso_week: str
    total_demand: int
    total_inventory: int
    projected_balance: int

class ShortageTrendPoint(BaseModel):
    iso_week: str
    shortage_count: int
    total_shortage_quantity: int
    critical_count: int

class SupplierPerformanceItem(BaseModel):
    supplier_id: str
    supplier_name: str
    rating: float
    on_time_delivery_rate: float
    allocated_capacity: int
    max_capacity: int
    utilization_pct: float

# ----------------- Data Quality / Exceptions Schemas -----------------
class DataQualityItem(BaseModel):
    issue_id: str
    scenario_id: Optional[str] = None
    issue_type: str
    severity: str
    affected_table: str
    affected_record_id: str
    expected_outcome: str
    actual_outcome: str
    detection_status: str
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
