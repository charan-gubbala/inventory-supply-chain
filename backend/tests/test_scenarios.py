import pytest
from datetime import datetime, date, timedelta
from backend.app.models.sku import SKU, SKUSubstitute
from backend.app.models.location import Location
from backend.app.models.inventory import UnitOfMeasureConversion
from backend.app.models.shortage import Shortage
from backend.app.services.inventory_service import InventoryService
from backend.app.services.mitigation_service import MitigationService

def test_scenario_1_duplicate_inbound_detection(db_session):
    """
    Scenario 1: Detect duplicate transaction receipt reference and prevent double counting.
    """
    sku = SKU(sku_id="SKU-SC1-001", name="Item SC1", category="INDUSTRIAL", cost_per_unit=10.0, price_per_unit=20.0, safety_stock_quantity=10, status="ACTIVE")
    loc = Location(location_id="LOC-SC1-001", name="Loc SC1", type="WAREHOUSE", capacity_units=10000, status="ACTIVE")
    db_session.add_all([sku, loc])
    db_session.commit()

    service = InventoryService(db_session)
    ref = "REF-DUPLICATE-TEST-001"

    # First transaction succeeds
    txn1 = service.record_transaction(sku.sku_id, loc.location_id, "RECEIPT", 100, reference_id=ref)
    assert txn1 is not None

    # Duplicate transaction with identical reference must be blocked
    with pytest.raises(ValueError) as exc:
        service.record_transaction(sku.sku_id, loc.location_id, "RECEIPT", 100, reference_id=ref)
    assert "Duplicate inbound transaction reference detected" in str(exc.value)

def test_scenario_2_unapproved_substitute_rejection(db_session):
    """
    Scenario 2: Reject unapproved substitute candidates.
    """
    sku1 = SKU(sku_id="SKU-SC2-001", name="Original Part", category="ELECTRONICS", cost_per_unit=30.0, price_per_unit=50.0, safety_stock_quantity=10, status="ACTIVE")
    sku2 = SKU(sku_id="SKU-SC2-002", name="Candidate Part", category="ELECTRONICS", cost_per_unit=32.0, price_per_unit=55.0, safety_stock_quantity=10, status="ACTIVE")
    loc = Location(location_id="LOC-SC2-001", name="Loc SC2", type="WAREHOUSE", capacity_units=10000, status="ACTIVE")
    sub = SKUSubstitute(
        substitute_id="SUB-SC2-TEST",
        original_sku_id=sku1.sku_id,
        substitute_sku_id=sku2.sku_id,
        approval_status="UNAPPROVED",
        conversion_rate=1.0,
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31)
    )
    shortage = Shortage(
        shortage_id="SHORT-SC2-001",
        sku_id=sku1.sku_id,
        location_id=loc.location_id,
        iso_week="2026W01",
        shortage_quantity=50,
        expected_shortage_date=date.today() + timedelta(days=5),
        root_cause="INSUFFICIENT_OPENING_INVENTORY",
        severity="HIGH",
        status="DETECTED"
    )
    db_session.add_all([sku1, sku2, loc, sub, shortage])
    db_session.commit()

    service = MitigationService(db_session)
    mitigations = service.generate_mitigations_for_shortage(shortage.shortage_id)

    # Find the substitute option
    sub_opts = [m for m in mitigations if m.strategy_type == "APPROVED_SUBSTITUTE"]
    assert len(sub_opts) == 1
    assert sub_opts[0].is_feasible is False
    assert "UNAPPROVED" in sub_opts[0].rejection_reason
    assert sub_opts[0].recommendation_score == 0.0

def test_scenario_5_uom_conversion():
    """
    Scenario 5: Unit of measure compatibility and approved conversions.
    """
    conv = UnitOfMeasureConversion(
        conversion_id="UOM-PALLET-UNITS",
        from_uom="PALLET",
        to_uom="UNITS",
        factor=240.0,
        is_active=True
    )
    pallets = 5
    units = pallets * float(conv.factor)
    assert units == 1200.0
