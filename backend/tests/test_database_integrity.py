import pytest
from datetime import datetime, date
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.supplier import Supplier
from backend.app.models.forecast_demand import ForecastDemand

def test_database_persistence_and_relationships(db_session):
    """
    Validates Requirement 2 & 18: Foreign keys, persistence, transactions.
    """
    # 1. Create SKU
    sku = SKU(
        sku_id="SKU-999001",
        name="Test Sensor",
        category="ELECTRONICS",
        unit_of_measure="UNITS",
        cost_per_unit=50.0,
        price_per_unit=85.0,
        safety_stock_quantity=20,
        status="ACTIVE"
    )
    db_session.add(sku)

    # 2. Create Location
    loc = Location(
        location_id="LOC-999001",
        name="Main Hub",
        type="WAREHOUSE",
        capacity_units=50000,
        status="ACTIVE"
    )
    db_session.add(loc)
    db_session.commit()

    # 3. Create Demand linking to SKU and Location
    demand = ForecastDemand(
        demand_id="DEM-SKU-999001-LOC-999001-2026W01",
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        iso_week="2026W01",
        forecast_quantity=150,
        demand_type="BASELINE",
        forecast_date=date(2026, 1, 1),
        confidence_level=95.0
    )
    db_session.add(demand)
    db_session.commit()

    # Query back
    fetched_demand = db_session.query(ForecastDemand).filter(
        ForecastDemand.demand_id == "DEM-SKU-999001-LOC-999001-2026W01"
    ).first()

    assert fetched_demand is not None
    assert fetched_demand.sku.name == "Test Sensor"
    assert fetched_demand.location.name == "Main Hub"
