# Testing Strategy & Verification Plan

## 1. Overview
The testing suite validates business logic, database integrity, mathematical balance reconciliation, exception handling, shortage detection, mitigation ranking, REST APIs, and data reproducibility.

---

## 2. Test Matrix Coverage (20 Mandatory Requirements)

| # | Test Area | Target Module | Scope |
|---|-----------|---------------|-------|
| 1 | Deterministic ID Generation | `tests/test_id_generation.py` | Verify regex patterns, zero-padding, and immutability |
| 2 | Foreign Key Integrity | `tests/test_database_integrity.py` | Verify referential integrity across all 11 core & supporting tables |
| 3 | Demand Generation | `tests/test_data_generator.py` | Verify seasonal patterns, spikes, and statistical properties |
| 4 | Inventory Calculations | `tests/test_inventory_service.py` | Verify opening, received, reserved, available, closing balance |
| 5 | Week-by-Week Balance Reconciliation | `tests/test_inventory_service.py` | Confirm closing stock week $w$ equals opening stock week $w+1$ |
| 6 | Duplicate Inbound Detection | `tests/test_scenarios.py` | Verify Scenario 1 duplicate transaction rejection and logging |
| 7 | Supplier Capacity Constraints | `tests/test_supplier_service.py` | Verify Scenario 3 supplier capacity boundary validation |
| 8 | Minimum Order Quantity (MOQ) | `tests/test_supplier_service.py` | Ensure orders enforce vendor MOQ threshold |
| 9 | Lead-Time Calculations | `tests/test_lead_time.py` | Validate order date + lead time = expected delivery |
| 10 | Transport Delays | `tests/test_lead_time.py` | Validate arrival date adjustment when delays occur |
| 11 | Production Capacity | `tests/test_production_service.py` | Ensure planned output respects plant machine hours |
| 12 | BOM Requirements | `tests/test_production_service.py` | Validate multi-level component availability check |
| 13 | Approved vs Unapproved Substitutes | `tests/test_scenarios.py` | Verify Scenario 2 unapproved substitute rejection |
| 14 | Unit of Measure (UOM) Conversion | `tests/test_scenarios.py` | Verify Scenario 5 UOM mismatch detection and conversion |
| 15 | Shortage Detection | `tests/test_shortage_service.py` | Verify shortage quantity equals abs(projected balance) and root causes |
| 16 | Mitigation Ranking & Feasibility | `tests/test_mitigation_service.py` | Verify 4 strategies, constraint rejection, and objective scoring |
| 17 | FastAPI REST Endpoints | `tests/test_api_endpoints.py` | Verify HTTP 200, schemas, pagination, filters, and transaction rollback |
| 18 | Database Persistence | `tests/test_database_integrity.py` | Verify commit, transactional updates, and rollback semantics |
| 19 | Ground Truth Evaluation | `tests/test_ground_truth.py` | Compare engine anomaly detections with ground-truth labels |
| 20 | Reproducibility Check | `tests/test_reproducibility.py` | Confirm seed 20261022 yields bitwise SHA-256 identical outputs |

---

## 3. Running Test Suites

Execute all pytest tests:
```bash
pytest backend/tests -v
```

Execute with coverage report:
```bash
pytest backend/tests -v --cov=backend/app --cov-report=term-missing
```
