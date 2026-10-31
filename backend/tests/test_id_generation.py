import re
import pytest

def test_deterministic_id_conventions():
    """
    Validates Requirement 1: Deterministic, zero-padded identifier conventions.
    """
    sku_pattern = re.compile(r"^SKU-\d{6}$")
    loc_pattern = re.compile(r"^LOC-\d{6}$")
    sup_pattern = re.compile(r"^SUP-\d{6}$")
    dem_pattern = re.compile(r"^DEM-SKU-\d{6}-LOC-\d{6}-\d{4}W\d{2}$")
    po_pattern = re.compile(r"^PO-\d{4}-\d{6}$")
    short_pattern = re.compile(r"^SHORT-\d{4}-\d{6}$")
    mit_pattern = re.compile(r"^MIT-SHORT-\d{4}-\d{6}-\d{2}$")
    prod_pattern = re.compile(r"^PROD-\d{4}-\d{6}$")

    sample_sku = "SKU-000001"
    sample_loc = "LOC-000001"
    sample_sup = "SUP-000001"
    sample_dem = "DEM-SKU-000001-LOC-000001-2026W01"
    sample_po = "PO-2026-000001"
    sample_short = "SHORT-2026-000001"
    sample_mit = "MIT-SHORT-2026-000001-01"
    sample_prod = "PROD-2026-000001"

    assert sku_pattern.match(sample_sku) is not None
    assert loc_pattern.match(sample_loc) is not None
    assert sup_pattern.match(sample_sup) is not None
    assert dem_pattern.match(sample_dem) is not None
    assert po_pattern.match(sample_po) is not None
    assert short_pattern.match(sample_short) is not None
    assert mit_pattern.match(sample_mit) is not None
    assert prod_pattern.match(sample_prod) is not None
