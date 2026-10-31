import pytest
from backend.app.main import root, health_check
from backend.app.routers.dashboard import get_dashboard_summary, get_inventory_trend, get_shortage_trend
from backend.app.routers.skus import list_skus
from backend.app.routers.locations import list_locations
from backend.app.routers.shortages import list_shortages
from backend.app.routers.validation import get_validation_results

def test_health_check_endpoints():
    res = root()
    assert res["status"] == "healthy"
    assert "version" in res
    assert res["docs_url"] == "/docs"

    health = health_check()
    assert health["status"] == "ok"

def test_dashboard_endpoints(db_session):
    summary = get_dashboard_summary(db=db_session)
    assert hasattr(summary, "total_skus")
    assert hasattr(summary, "total_shortages")
    assert hasattr(summary, "supplier_capacity_utilization_pct")

    trend = get_inventory_trend(db=db_session)
    assert isinstance(trend, list)

    s_trend = get_shortage_trend(db=db_session)
    assert isinstance(s_trend, list)

def test_skus_and_locations_endpoints(db_session):
    skus = list_skus(skip=0, limit=10, db=db_session)
    assert isinstance(skus, list)

    locs = list_locations(skip=0, limit=10, db=db_session)
    assert isinstance(locs, list)

def test_shortages_and_validation_endpoints(db_session):
    shortages = list_shortages(skip=0, limit=10, db=db_session)
    assert isinstance(shortages, list)

    val_res = get_validation_results(db=db_session)
    assert "total_records_checked" in val_res
    assert "passed_checks" in val_res
    assert "anomalies_detected" in val_res
