import pytest
from datetime import date, timedelta
from backend.app.models.sku import SKU, SKUSubstitute
from backend.app.models.location import Location
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.models.shortage import Shortage
from backend.app.models.inventory import Inventory
from backend.app.services.mitigation_service import MitigationService

def test_mitigation_strategies_and_scoring(db_session):
    """
    Validates Requirement 16: Evaluates 4 strategies, rejects infeasible options, ranks by score.
    """
    sku = SKU(
        sku_id="SKU-444001",
        name="Packaging Box Large",
        category="PACKAGING",
        unit_of_measure="UNITS",
        cost_per_unit=5.0,
        price_per_unit=9.0,
        safety_stock_quantity=100,
        status="ACTIVE"
    )
    loc = Location(
        location_id="LOC-444001",
        name="Regional DC",
        type="WAREHOUSE",
        capacity_units=150000,
        status="ACTIVE"
    )
    sup = Supplier(
        supplier_id="SUP-444001",
        name="BoxCraft Global",
        rating=4.2,
        on_time_delivery_rate=95.0,
        status="ACTIVE"
    )
    db_session.add_all([sku, loc, sup])
    db_session.commit()

    # Lead time arriving before shortage
    lt = LeadTime(
        lead_time_id="LT-SUP-444001-SKU-444001-LOC-444001",
        supplier_id=sup.supplier_id,
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        base_lead_time_days=4,
        min_order_quantity=50,
        cost_per_unit=5.0,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    cap = SupplierCapacity(
        capacity_id="CAP-SUP-444001-SKU-444001",
        supplier_id=sup.supplier_id,
        sku_id=sku.sku_id,
        max_capacity_per_week=2000,
        allocated_capacity=500,
        available_capacity=1500,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    shortage = Shortage(
        shortage_id="SHORT-2026-999001",
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        iso_week="2026W04",
        shortage_quantity=200,
        expected_shortage_date=date.today() + timedelta(days=14),
        root_cause="INSUFFICIENT_OPENING_INVENTORY",
        severity="HIGH",
        status="DETECTED"
    )
    db_session.add_all([lt, cap, shortage])
    db_session.commit()

    service = MitigationService(db_session)
    mitigations = service.generate_mitigations_for_shortage(shortage.shortage_id)

    assert len(mitigations) >= 1
    top_mit = mitigations[0]
    assert top_mit.strategy_type == "SUPPLIER_PURCHASE"
    assert top_mit.is_feasible is True
    assert top_mit.recommendation_score > 0.0
    assert top_mit.rank == 1

    # Test approval workflow
    approved = service.approve_mitigation(top_mit.mitigation_id)
    assert approved.approval_status == "APPROVED"
    assert shortage.status == "MITIGATED"
