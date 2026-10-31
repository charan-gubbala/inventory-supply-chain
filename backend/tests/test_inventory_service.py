import pytest
from datetime import date
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.services.inventory_service import InventoryService

def test_inventory_calculation_and_horizon_reconciliation(db_session):
    """
    Validates Requirements 4 & 5:
    Closing Stock = Opening Stock + Received Stock - Demand - Adjustments
    Next week Opening Stock = previous week Closing Stock.
    """
    sku = SKU(
        sku_id="SKU-888001",
        name="Industrial Motor",
        category="INDUSTRIAL",
        unit_of_measure="UNITS",
        cost_per_unit=120.0,
        price_per_unit=180.0,
        safety_stock_quantity=30,
        status="ACTIVE"
    )
    loc = Location(
        location_id="LOC-888001",
        name="East Logistics Center",
        type="WAREHOUSE",
        capacity_units=80000,
        status="ACTIVE"
    )
    db_session.add_all([sku, loc])
    db_session.commit()

    # Create demand for 3 consecutive weeks
    weeks = ["2026W01", "2026W02", "2026W03"]
    demands = [100, 150, 80]
    for w, d_qty in zip(weeks, demands):
        dem = ForecastDemand(
            demand_id=f"DEM-SKU-888001-LOC-888001-{w}",
            sku_id=sku.sku_id,
            location_id=loc.location_id,
            iso_week=w,
            forecast_quantity=d_qty,
            demand_type="BASELINE",
            forecast_date=date(2026, 1, 1),
            confidence_level=95.0
        )
        db_session.add(dem)
    db_session.commit()

    service = InventoryService(db_session)
    reconciled = service.reconcile_horizon(
        sku_id=sku.sku_id,
        location_id=loc.location_id,
        ordered_weeks=weeks,
        initial_opening_stock=500
    )

    assert len(reconciled) == 3

    # Week 1: Opening=500, Demand=100, Closing=400
    assert reconciled[0].opening_stock == 500
    assert reconciled[0].closing_stock == 400

    # Week 2: Opening must equal Week 1 Closing (400), Demand=150, Closing=250
    assert reconciled[1].opening_stock == 400
    assert reconciled[1].closing_stock == 250

    # Week 3: Opening must equal Week 2 Closing (250), Demand=80, Closing=170
    assert reconciled[2].opening_stock == 250
    assert reconciled[2].closing_stock == 170
