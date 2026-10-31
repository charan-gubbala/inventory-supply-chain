import pytest
from datetime import date
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.production_plan import BOMHeader, BOMComponent, ProductionCapacity

def test_production_capacity_and_bom_requirements(db_session):
    """
    Validates Requirements 11 & 12: Production capacity hours and BOM components.
    """
    finished_sku = SKU(
        sku_id="SKU-666001",
        name="Finished Drone",
        category="ELECTRONICS",
        unit_of_measure="UNITS",
        cost_per_unit=300.0,
        price_per_unit=550.0,
        safety_stock_quantity=10,
        status="ACTIVE"
    )
    comp_sku1 = SKU(
        sku_id="SKU-666002",
        name="Rotor Blade",
        category="INDUSTRIAL",
        unit_of_measure="UNITS",
        cost_per_unit=15.0,
        price_per_unit=25.0,
        safety_stock_quantity=50,
        status="ACTIVE"
    )
    comp_sku2 = SKU(
        sku_id="SKU-666003",
        name="Lithium Battery Pack",
        category="ELECTRONICS",
        unit_of_measure="UNITS",
        cost_per_unit=45.0,
        price_per_unit=75.0,
        safety_stock_quantity=30,
        status="ACTIVE"
    )
    plant = Location(
        location_id="LOC-666001",
        name="Assembly Plant Gamma",
        type="PLANT",
        capacity_units=200000,
        status="ACTIVE"
    )
    db_session.add_all([finished_sku, comp_sku1, comp_sku2, plant])
    db_session.commit()

    # BOM Header
    bom = BOMHeader(
        bom_id="BOM-SKU-666001-V1",
        finished_sku_id=finished_sku.sku_id,
        name="Drone Assembly BOM",
        version="1.0",
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
        is_active=True
    )
    db_session.add(bom)
    db_session.flush()

    # BOM Components (4 rotors, 1 battery)
    c1 = BOMComponent(
        component_id="BOMC-1",
        bom_id=bom.bom_id,
        component_sku_id=comp_sku1.sku_id,
        quantity_required=4.0,
        unit_of_measure="UNITS",
        scrap_rate=0.0
    )
    c2 = BOMComponent(
        component_id="BOMC-2",
        bom_id=bom.bom_id,
        component_sku_id=comp_sku2.sku_id,
        quantity_required=1.0,
        unit_of_measure="UNITS",
        scrap_rate=0.0
    )
    db_session.add_all([c1, c2])

    # Plant capacity
    pcap = ProductionCapacity(
        prod_capacity_id="PCAP-LOC-666001-2026W01",
        location_id=plant.location_id,
        iso_week="2026W01",
        max_hours=168.0,
        allocated_hours=100.0,
        available_hours=68.0,
        units_per_hour=5.0
    )
    db_session.add(pcap)
    db_session.commit()

    # Verify BOM lookup
    fetched_bom = db_session.query(BOMHeader).filter(BOMHeader.finished_sku_id == finished_sku.sku_id).first()
    assert fetched_bom is not None
    assert len(fetched_bom.components) == 2

    # Verify component calculation for 50 drones:
    # 50 * 4 = 200 rotors, 50 * 1 = 50 batteries
    rotor_needed = 50 * float(c1.quantity_required)
    battery_needed = 50 * float(c2.quantity_required)
    assert rotor_needed == 200.0
    assert battery_needed == 50.0

    # Hours required: 50 / 5 units/hr = 10 hrs <= available 68 hrs
    hours_req = 50 / float(pcap.units_per_hour)
    assert hours_req == 10.0
    assert hours_req <= float(pcap.available_hours)
