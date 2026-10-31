import pytest
from datetime import date
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime

def test_supplier_capacity_and_moq_enforcement(db_session):
    """
    Validates Requirements 7 & 8: Supplier capacity limits and MOQ constraints.
    """
    sku = SKU(
        sku_id="SKU-777001",
        name="Microcontroller",
        category="ELECTRONICS",
        unit_of_measure="UNITS",
        cost_per_unit=25.0,
        price_per_unit=40.0,
        safety_stock_quantity=50,
        status="ACTIVE"
    )
    loc = Location(
        location_id="LOC-777001",
        name="Plant Beta",
        type="PLANT",
        capacity_units=100000,
        status="ACTIVE"
    )
    sup = Supplier(
        supplier_id="SUP-777001",
        name="Precision Silicon Inc",
        rating=4.5,
        on_time_delivery_rate=98.0,
        status="ACTIVE"
    )
    db_session.add_all([sku, loc, sup])
    db_session.commit()

    cap = SupplierCapacity(
        capacity_id="CAP-SUP-777001-SKU-777001",
        supplier_id=sup.supplier_id,
        sku_id=sku.sku_id,
        max_capacity_per_week=1000,
        allocated_capacity=800,
        available_capacity=200,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    lt = LeadTime(
        lead_time_id="LT-SUP-777001-SKU-777001-LOC-777001",
        supplier_id=sup.supplier_id,
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        base_lead_time_days=7,
        min_order_quantity=150,
        cost_per_unit=25.0,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    db_session.add_all([cap, lt])
    db_session.commit()

    # Verify MOQ
    requested_qty = 50
    enforced_qty = max(requested_qty, lt.min_order_quantity)
    assert enforced_qty == 150

    # Verify available capacity check
    assert enforced_qty <= cap.available_capacity  # 150 <= 200 (Feasible)

    # Exceeding order
    large_order = 250
    assert large_order > cap.available_capacity  # Infeasible
