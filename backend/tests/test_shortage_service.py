import pytest
from datetime import date
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.inventory import Inventory
from backend.app.models.lead_time import LeadTime
from backend.app.models.supplier import Supplier
from backend.app.services.shortage_service import ShortageService

def test_shortage_detection_and_severity(db_session):
    """
    Validates Requirement 15:
    Shortage occurs when Projected Available Balance < 0.
    Shortage quantity equals abs(projected balance).
    Severity based on deficit to demand ratio.
    """
    sku = SKU(
        sku_id="SKU-555001",
        name="Critical Surgical Kit",
        category="PHARMA",
        unit_of_measure="UNITS",
        cost_per_unit=200.0,
        price_per_unit=350.0,
        safety_stock_quantity=50,
        status="ACTIVE"
    )
    loc = Location(
        location_id="LOC-555001",
        name="Medical Logistics Hub",
        type="WAREHOUSE",
        capacity_units=90000,
        status="ACTIVE"
    )
    sup = Supplier(
        supplier_id="SUP-555001",
        name="MediPharm Supplies",
        rating=4.8,
        on_time_delivery_rate=99.0,
        status="ACTIVE"
    )
    db_session.add_all([sku, loc, sup])
    db_session.commit()

    lt = LeadTime(
        lead_time_id="LT-SUP-555001-SKU-555001-LOC-555001",
        supplier_id=sup.supplier_id,
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        base_lead_time_days=6,
        min_order_quantity=50,
        cost_per_unit=200.0,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    # Demand = 750
    demand = ForecastDemand(
        demand_id="DEM-SKU-555001-LOC-555001-2026W01",
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        iso_week="2026W01",
        forecast_quantity=750,
        demand_type="SPIKE",
        forecast_date=date(2026, 1, 1),
        confidence_level=95.0
    )
    # Opening Stock = 500, Incoming = 100, Demand = 750 -> Projected = -150
    inv = Inventory(
        inventory_id="INV-SKU-555001-LOC-555001-2026W01",
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        iso_week="2026W01",
        opening_stock=500,
        received_stock=0,
        reserved_stock=0,
        available_stock=500,
        incoming_stock=100,
        adjustments=0,
        closing_stock=-250,
        projected_available_balance=-150,
        unit_of_measure="UNITS"
    )
    db_session.add_all([lt, demand, inv])
    db_session.commit()

    service = ShortageService(db_session)
    shortages = service.detect_shortages(iso_week="2026W01")

    assert len(shortages) == 1
    shortage = shortages[0]
    assert shortage.sku_id == "SKU-555001"
    assert shortage.shortage_quantity == 150
    assert shortage.root_cause == "DEMAND_SPIKE"
    # Ratio: 150 / 750 = 20% -> MEDIUM severity
    assert shortage.severity == "MEDIUM"
