# End-to-End Inventory & Supply Chain Demand Planning System

An enterprise-grade, production-style Inventory and Supply Chain Demand Planning System that synchronizes customer demand forecasts with on-hand inventory, in-transit purchase orders, supplier capacity, vendor lead times, plant assembly capacity, and multi-level Bills of Materials (BOM).

The system features an automated **Time-Phased Inventory Balancing Engine**, **Explainable Shortage Detection**, a **Multi-Strategy Mitigation Recommendation Engine**, an automated **15-Point Data Validation Engine**, and a modern **React Operations Dashboard**.

---

## Table of Contents
1. [Business Problem & Objectives](#1-business-problem--objectives)
2. [Key Capabilities & Features](#2-key-capabilities--features)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture & Folder Structure](#4-system-architecture--folder-structure)
5. [Database Schema & 11 Core Entities](#5-database-schema--11-core-entities)
6. [Core Supply Chain Business Logic](#6-core-supply-chain-business-logic)
7. [The 5 Controlled Exception Scenarios & Ground Truth](#7-the-5-controlled-exception-scenarios--ground-truth)
8. [Installation & Setup](#8-installation--setup)
9. [Running the Application](#9-running-the-application)
10. [Docker & Containerized Deployment](#10-docker--containerized-deployment)
11. [Data Generation, Validation & Reproducibility](#11-data-generation-validation--reproducibility)
12. [Automated Testing](#12-automated-testing)
13. [API Documentation](#13-api-documentation)
14. [Export Functionality](#14-export-functionality)
15. [Project Limitations & Future Enhancements](#15-project-limitations--future-enhancements)
16. [Publishing to GitHub](#16-publishing-to-github)

---

## 1. Business Problem & Objectives

In discrete and process supply chains, mismatches between forecasted demand and procurement timelines lead to costly stockouts or excess holding costs. Disparate lead times, delayed carrier shipments, supplier capacity bottlenecks, and Bill of Materials component shortages frequently cascade into critical fulfillment failures.

### Primary Objectives:
- **Balance Supply & Demand:** Dynamically compute time-phased stock levels ($PAB$) across rolling weekly horizons.
- **Explainable Shortage Attribution:** Distinguish root causes (demand spikes, supplier limits, production bottlenecks, missing lead times, transport delays) rather than treating deficits as opaque numbers.
- **Prescriptive Mitigations:** Generate, rank, and score feasible remediation actions across four core supply chain levers:
  1. Vendor purchase orders.
  2. Inter-warehouse transfers.
  3. Additional factory production (BOM assemblies).
  4. Approved product substitutions.
- **Data Quality Audits:** Automatically audit referential integrity, duplicate inbounds, unapproved substitutions, and unit of measure discrepancies.

### Target Personas:
- **Inventory Planner:** Balances weekly stock and reviews time-phased balance trajectories.
- **Logistics Analyst:** Tracks purchase orders, shipments, and carrier transit delays.
- **Operations Manager:** Evaluates supplier capacity utilization, factory throughput, and approves mitigations.
- **Warehouse Operator:** Manages receipt transactions and inter-facility transfers.
- **Supplier Coordinator:** Monitors supplier ratings, contracts, lead times, and MOQs.

---

## 2. Key Capabilities & Features

- **Strict Inventory Balancing Formula:**
  $$\text{Closing Stock}_w = \text{Opening Stock}_w + \text{Received Stock}_w - \text{Demand}_w - \text{Adjustments}_w$$
  with temporal continuity strictly enforced: $\text{Opening Stock}_{w+1} = \text{Closing Stock}_w$.
- **Projected Available Balance (PAB):** Time-phased projection including scheduled inbound POs, factory production receipts, and incoming transfers.
- **Shortage Detection Engine:** Automated trigger whenever $PAB < 0$. Severity scored into `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW`.
- **Mitigation Scoring & Ranking:** Evaluates cost efficiency, lead-time slack, supplier risk, and customer service impact using a documented objective function.
- **5 Controlled Negative Scenarios:** Injected anomalies (duplicate receipts, unapproved substitutes, capacity breaches, missing lead times, UOM mismatches) validated against a separated ground-truth dataset.
- **100% Bitwise Reproducibility:** Verified SHA-256 and row-count reproducibility with fixed random seed `20261022`.
- **FastAPI Backend (45 REST endpoints):** Modular routers with Pydantic v2 schemas and SQLAlchemy 2.x ORM models.
- **Interactive React Dashboard (12 pages):** Built with Vite, Tailwind CSS, Lucide React, and Recharts.

---

## 3. Technology Stack

### Backend
- **Python 3.11+ / 3.12+**
- **FastAPI:** High-performance RESTful API framework
- **SQLAlchemy 2.x:** Modern relational ORM
- **Alembic:** Database migrations
- **Pydantic v2:** Request/response validation
- **Pandas & NumPy:** Time-series demand and statistical generation
- **Faker:** Realistic vendor, address, and product catalog synthesis

### Database
- **PostgreSQL 16** (production / Docker Compose)
- **SQLite 3** (local standalone zero-config option with foreign key PRAGMAs)

### Frontend
- **React.js 18**
- **Vite 6**
- **Tailwind CSS 3**
- **Axios**
- **React Router 6**
- **Recharts:** Interactive area, bar, and performance charts
- **Lucide React:** Iconography

### Testing & Verification
- **Pytest 8.x**
- **FastAPI TestClient & HTTPX**

### Containerization & Tooling
- **Docker & Docker Compose**
- **Git**

---

## 4. System Architecture & Folder Structure

```text
inventory-supply-chain/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application bootstrap & CORS setup
│   │   ├── config.py                   # Pydantic settings & database URL resolver
│   │   ├── database.py                 # SQLAlchemy engine, sessionmaker & init_db
│   │   │
│   │   ├── models/                     # SQLAlchemy 2.x ORM models
│   │   │   ├── sku.py                  # SKU, SKUSubstitute, SKULocation
│   │   │   ├── location.py             # Location facilities
│   │   │   ├── forecast_demand.py      # Weekly customer demand
│   │   │   ├── inventory.py            # Balances, transactions & UOM conversions
│   │   │   ├── supplier.py             # Supplier catalog
│   │   │   ├── supplier_capacity.py    # Supplier capacity limits
│   │   │   ├── lead_time.py            # Lead times, MOQs & contract prices
│   │   │   ├── purchase_order.py       # POs, lines, shipments & transport delays
│   │   │   ├── production_plan.py      # Production plans, BOM headers & components
│   │   │   ├── shortage.py             # Detected shortages & root causes
│   │   │   ├── mitigation_option.py    # Mitigation recommendations & transfers
│   │   │   └── additional_models.py    # EventHistory & DataQualityIssue
│   │   │
│   │   ├── schemas/                    # Pydantic request & response schemas
│   │   │   └── schemas.py              # Strongly-typed DTOs
│   │   │
│   │   ├── routers/                    # REST API endpoints
│   │   │   ├── dashboard.py            # Executive KPIs, trends & performance
│   │   │   ├── skus.py                 # SKU catalog & substitute lookups
│   │   │   ├── locations.py            # Facility locations
│   │   │   ├── demand.py               # Time-phased demand queries
│   │   │   ├── inventory.py            # Stock balances & lane summaries
│   │   │   ├── suppliers.py            # Supplier performance & capacities
│   │   │   ├── purchase_orders.py      # Inbound PO lifecycle
│   │   │   ├── production.py           # Assembly schedules & BOMs
│   │   │   ├── shortages.py            # Shortage detection & inspection
│   │   │   ├── mitigations.py          # Approve & reject recommendations
│   │   │   ├── validation.py           # 15-point validation engine trigger
│   │   │   ├── data_generation.py      # Synthetic generation trigger & status
│   │   │   ├── exports.py              # CSV/JSON file downloads
│   │   │   └── exceptions.py           # Quality audits & scenario evaluations
│   │   │
│   │   └── services/                   # Business logic calculation services
│   │       ├── inventory_service.py    # Balancing & week-by-week reconciliation
│   │       ├── shortage_service.py     # Shortage detection & root cause diagnosis
│   │       ├── mitigation_service.py   # Multi-strategy ranking & scoring
│   │       ├── validation_service.py   # 15 automated validation checks
│   │       ├── demand_service.py       # Demand aggregations
│   │       ├── supplier_service.py     # Vendor constraints & MOQs
│   │       └── production_service.py   # BOM & plant capacity logic
│   │
│   ├── tests/                          # Automated pytest suite (17 comprehensive tests)
│   ├── alembic/                        # Database migration scripts
│   ├── requirements.txt                # Backend dependencies
│   └── Dockerfile                      # Backend container definition
│
├── frontend/
│   ├── src/
│   │   ├── layouts/
│   │   │   └── MainLayout.jsx          # Sidebar, top navigation, active status
│   │   ├── pages/                      # 12 Interactive Dashboard Views
│   │   │   ├── DashboardPage.jsx       # KPIs, area/bar charts & supplier table
│   │   │   ├── SKUPage.jsx             # SKU catalog, categories, substitute modal
│   │   │   ├── LocationPage.jsx        # Plants, distribution centers, warehouses
│   │   │   ├── DemandPage.jsx          # Forecast demand filters & patterns
│   │   │   ├── InventoryPage.jsx       # Time-phased stock levels & PAB highlights
│   │   │   ├── SupplierPage.jsx        # Supplier profiles, ratings, capacities drawer
│   │   │   ├── PurchaseOrderPage.jsx   # PO lifecycle, status updater, create modal
│   │   │   ├── ProductionPage.jsx      # Plant schedules, BOM component lookups
│   │   │   ├── ShortagePage.jsx        # Shortage detection, diagnostic drawer
│   │   │   ├── MitigationPage.jsx      # Multi-strategy cards with Approve/Reject
│   │   │   ├── ExceptionsPage.jsx      # 5 Controlled scenarios vs Ground Truth
│   │   │   └── DataOpsPage.jsx         # Generation, validation suite, exports
│   │   ├── services/
│   │   │   └── api.js                  # Axios client & typed service endpoints
│   │   ├── App.jsx                     # Route declarations
│   │   ├── main.jsx                    # Root React DOM bootstrap
│   │   └── index.css                   # Tailwind styling
│   ├── package.json                    # Frontend dependencies
│   ├── vite.config.js                  # Vite server & API proxy
│   └── Dockerfile                      # Multi-stage Nginx container
│
├── data/
│   ├── generated/                      # Generated dataset files
│   ├── exports/                        # Exported CSV, JSON, and SQL seed files
│   ├── ground_truth/                   # Isolated Ground Truth CSV & JSON
│   └── manifests/                      # Source provenance & dataset manifest
│
├── scripts/
│   ├── generate_data.py                # Synthetic generator (Starter & Full modes)
│   ├── validate_data.py                # Automated 15-point validation runner
│   ├── export_data.py                  # Full CSV, JSON, and SQL export script
│   ├── reproducibility_check.py        # Dual-run bitwise SHA-256 verification
│   └── seed_database.py                # Database reset and population
│
├── docs/
│   ├── DATA_DICTIONARY.md              # Complete data dictionary for all entities
│   ├── DATABASE_SCHEMA.md              # ER diagram, cardinalities & indexes
│   ├── BUSINESS_RULES.md               # Mathematical balance formulas & logic
│   ├── DATA_GENERATION.md              # Statistical distributions & seed spec
│   └── TESTING.md                      # Test matrix & coverage documentation
│
├── docker-compose.yml                  # Multi-service composition (DB, API, Web)
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
└── requirements.txt                    # Project dependencies
```

---

## 5. Database Schema & 11 Core Entities

The system implements 11 core tables and 8 supporting tables:

1. **`SKU` (`skus`):** Master product catalog with categories, unit costs, selling prices, and safety stocks.
2. **`Location` (`locations`):** Manufacturing plants, distribution centers, and warehouses with physical capacities.
3. **`ForecastDemand` (`forecast_demands`):** Time-phased customer demand records with demand drivers (`BASELINE`, `SEASONAL`, `SPIKE`, `PROMOTION`).
4. **`Inventory` (`inventory_balances`):** Weekly snapshot tracking opening, received, reserved, available, incoming, closing stock, and projected available balance ($PAB$).
5. **`Supplier` (`suppliers`):** Vendor directory with quality ratings and on-time delivery percentages.
6. **`SupplierCapacity` (`supplier_capacities`):** Time-bounded weekly capacity limits per supplier and SKU.
7. **`LeadTime` (`lead_times`):** Contracted vendor delivery lead times, minimum order quantities (MOQ), and purchase prices.
8. **`PurchaseOrder` (`purchase_orders`):** Inbound procurement orders with lifecycle progression: `CREATED` $\rightarrow$ `APPROVED` $\rightarrow$ `SHIPPED` $\rightarrow$ `RECEIVED`.
9. **`ProductionPlan` (`production_plans`):** Internal plant manufacturing schedules.
10. **`Shortage` (`shortages`):** Automatically detected deficits ($PAB < 0$) with diagnostic root causes and severity tiers.
11. **`MitigationOption` (`mitigation_options`):** Actionable remediation recommendations ranked by an objective scoring function.

### Supporting Tables:
- **`SKUSubstitute`:** Alternative SKU relationships with approval flags (`APPROVED`, `UNAPPROVED`, `PENDING`).
- **`BOMHeader` & `BOMComponent`:** Multi-level assembly structures and component scrap rates.
- **`ProductionCapacity`:** Factory labor and machine hours per week.
- **`WarehouseTransfer`:** Inter-facility stock movements.
- **`PurchaseOrderLine`:** Line-item breakdown.
- **`Shipment` & `TransportDelay`:** Carrier logistics tracking and logged port/customs delays.
- **`InventoryTransaction`:** Auditable transactional ledger.
- **`EventHistory`:** Immutable audit log of domain events.
- **`DataQualityIssue`:** Logged data anomalies and validation failures.
- **`UnitOfMeasureConversion`:** Conversion ratios between packaging units (`PALLET`, `BOX`, `UNITS`, `KG`, `LITER`).

*Detailed schemas, constraints, and data dictionaries are available in [docs/DATA_DICTIONARY.md](file:///docs/DATA_DICTIONARY.md) and [docs/DATABASE_SCHEMA.md](file:///docs/DATABASE_SCHEMA.md).*

---

## 6. Core Supply Chain Business Logic

### Inventory Balance Reconciliation
Every weekly inventory snapshot is reconciled using:
$$\text{Closing Stock}_w = \text{Opening Stock}_w + \text{Received Stock}_w - \text{Demand}_w - \text{Adjustments}_w$$
$$\text{Available Stock}_w = \max(0, \text{Opening Stock}_w + \text{Received Stock}_w - \text{Reserved Stock}_w)$$
$$\text{Projected Available Balance (PAB)}_w = \text{Available Stock}_w + \text{Incoming Inbound}_w - \text{Forecast Demand}_w$$

### Shortage Detection & Root Cause Analysis
Whenever $PAB_w < 0$, a shortage is registered for $\text{Shortage Quantity} = |PAB_w|$.
The engine deterministically attributes one of six root causes:
1. `DEMAND_SPIKE`: Demand in week $w > 1.8 \times$ historical mean for the SKU.
2. `DELAYED_SHIPMENT`: Inbound shipment scheduled for this period suffered carrier or customs delays.
3. `SUPPLIER_CAPACITY_CONSTRAINT`: Sourcing blocked because vendor allocated capacity is 100% committed.
4. `PRODUCTION_CAPACITY_CONSTRAINT`: Plant machine hours exhausted or BOM components deficient.
5. `MISSING_LEAD_TIME`: Sourcing blocked due to unconfigured lead time lanes.
6. `INSUFFICIENT_OPENING_INVENTORY`: Baseline demand exceeded opening safety stock buffers.

### Multi-Strategy Mitigation Recommendations
Four strategies are evaluated for each shortage:
1. **Supplier Purchase:** Checks active status, lead time arrival date $\le$ shortage deadline, MOQ enforcement, and available supplier capacity.
2. **Warehouse Stock Transfer:** Identifies sister warehouses with surplus inventory above safety stocks.
3. **Additional Production:** Evaluates plant hour availability and verifies stock levels for all raw components listed in `BOMComponent`.
4. **Approved Substitute SKU:** Evaluates alternate items with `approval_status == 'APPROVED'`, factoring in unit conversion rates.

Infeasible options are marked with explicit rejection reasons (e.g., "Supplier capacity exceeded", "Substitute candidate is UNAPPROVED", "Delivery arrives after shortage deadline"). Feasible options are scored on a 0–100 scale using customer service impact, cost efficiency, lead-time buffer, and supplier risk.

---

## 7. The 5 Controlled Exception Scenarios & Ground Truth

To prove system robustness and validation fidelity, five deliberate negative exception scenarios are injected into the dataset and verified against an isolated ground-truth file (`data/ground_truth/ground_truth.json`):

| Scenario | Issue Type | Injection Mechanism | Expected System Decision | Observed Behavior |
|---|---|---|---|---|
| **Scenario 1** | `DUPLICATE_INBOUND` | Injected duplicate receipt transaction reference for PO-2026-000001 | `REJECT_TRANSACTION` | Blocked duplicate addition, logged `DataQualityIssue`, preserved balance integrity. |
| **Scenario 2** | `UNAPPROVED_SUBSTITUTE` | Registered candidate substitute SKU flagged as `UNAPPROVED` | `REJECT_SUBSTITUTION` | Excluded from feasible mitigations, flagged in quality audit. |
| **Scenario 3** | `CAPACITY_EXCEEDED` | Attempted order volume exceeding supplier maximum capacity | `REJECT_ORDER` | Marked option infeasible, logged capacity breach anomaly. |
| **Scenario 4** | `MISSING_LEAD_TIME` | Purposely deleted lead time lane for SKU-000002 at LOC-000002 | `BLOCK_MITIGATION` | Refused zero-day delivery assumption, marked sourcing blocked. |
| **Scenario 5** | `UOM_MISMATCH` | Incompatible unit arithmetic attempted without active conversion | `REJECT_CALCULATION` | Prevented corrupted stock additions without approved conversion factor. |

Ground truth data is stored strictly outside operational inputs to prevent label leakage.

---

## 8. Installation & Setup

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ and npm
- Git
- (Optional) Docker & Docker Compose

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/inventory-supply-chain.git
cd inventory-supply-chain
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
```
*(By default, the application runs on SQLite for instant local execution. Set `DATABASE_URL` in `.env` to connect to PostgreSQL).*

### 3. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cd ..
```

### 4. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## 9. Running the Application

### Step 1: Initialize Database & Run Migrations
```bash
# Run Alembic migrations
alembic -c backend/alembic.ini upgrade head
```

### Step 2: Seed Synthetic Supply Chain Data
```bash
# Generate starter dataset (10 SKUs, 3 locations, 5 suppliers, 4 weeks)
python scripts/generate_data.py --mode starter --seed 20261022

# Or generate full scale dataset (3,000 SKUs, 50 locations, 52 weeks)
# python scripts/generate_data.py --mode full --seed 20261022
```

### Step 3: Start the FastAPI Backend
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The REST API will be available at: **http://localhost:8000**  
Interactive Swagger documentation: **http://localhost:8000/docs**

### Step 4: Start the React Frontend Dashboard
In a separate terminal:
```bash
cd frontend
npm run dev
```
The operations dashboard will be accessible at: **http://localhost:5173**

---

## 10. Docker & Containerized Deployment

To launch the full PostgreSQL, FastAPI, and React stack with a single command:

```bash
docker compose up -d --build
```

Services initialized:
- **PostgreSQL 16 Database:** `localhost:5432`
- **FastAPI Backend:** `http://localhost:8000`
- **React Nginx Frontend:** `http://localhost:3000`

To tear down:
```bash
docker compose down -v
```

---

## 11. Data Generation, Validation & Reproducibility

### Synthetic Generation Script
```bash
# Starter mode (fast, lightweight for UI development)
python scripts/generate_data.py --mode starter --seed 20261022

# Full scale mode
python scripts/generate_data.py --mode full --seed 20261022
```

### Automated 15-Point Validation Runner
```bash
python scripts/validate_data.py
```
Checks performed:
1. Primary-key uniqueness
2. Foreign-key referential integrity
3. Required field non-nullability
4. Allowed status enumerations
5. Date ordering consistency
6. Inventory closing stock arithmetic reconciliation
7. Purchase order lifecycle validation
8. Duplicate inbound receipt detection
9. Supplier capacity threshold validation
10. Lead-time completeness across lanes
11. Multi-level BOM availability
12. Unit-of-measure conversion compatibility
13. Substitute approval status validation
14. Mitigation feasibility integrity
15. Event-history audit consistency

Reports are exported to `data/exports/validation_report.json` and `data/exports/validation_report.csv`.

### Reproducibility Verification
```bash
python scripts/reproducibility_check.py
```
Executes two independent end-to-end data generation runs with fixed seed `20261022` and validates that line counts and SHA-256 checksums match identically across every table and ground-truth file.

---

## 12. Automated Testing

Run the full pytest suite:
```bash
pytest backend/tests -v
```

### Test Coverage Highlights:
- `test_id_generation.py`: Deterministic zero-padded regex ID patterns (`SKU-000001`, `PO-2026-000001`, `SHORT-2026-000001`).
- `test_database_integrity.py`: Foreign key integrity and commit persistence.
- `test_inventory_service.py`: Week-by-week stock reconciliation and balance carryover.
- `test_lead_time.py`: Sourcing lead times and transport delays.
- `test_supplier_service.py`: Supplier capacity constraints and MOQ enforcement.
- `test_production_service.py`: BOM multi-component requirements and plant hour limits.
- `test_shortage_service.py`: Shortage detection and diagnostic root-cause classification.
- `test_mitigation_service.py`: 4 mitigation strategies, feasibility pruning, and scoring.
- `test_scenarios.py`: All 5 negative exception scenarios.
- `test_api_endpoints.py`: REST endpoint responses and schema validations.
- `test_ground_truth.py`: Ground truth dataset structure and scenario mapping.
- `test_reproducibility.py`: Verified reproducibility report artifact.

---

## 13. API Documentation

Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### Primary Endpoints:
| Method | Route | Description |
|---|---|---|
| `GET` | `/api/dashboard/summary` | Real-time aggregate KPIs |
| `GET` | `/api/dashboard/inventory-trend` | Weekly demand vs. available stock |
| `GET` | `/api/dashboard/shortage-trend` | Weekly deficit counts and quantities |
| `GET` | `/api/dashboard/supplier-performance` | Vendor ratings and capacity utilization |
| `GET` | `/api/skus` | SKU master list with search and filters |
| `GET` | `/api/skus/{sku_id}/substitutes` | Approved and unapproved substitute candidates |
| `GET` | `/api/locations` | Facility network listing |
| `GET` | `/api/demand` | Filtered weekly customer demand projections |
| `GET` | `/api/inventory` | Inventory balances (with `shortage_only` filter) |
| `GET` | `/api/suppliers` | Supplier catalog with capacity details |
| `GET` | `/api/purchase-orders` | Inbound orders lifecycle |
| `POST` | `/api/purchase-orders` | Issue new purchase order |
| `PATCH` | `/api/purchase-orders/{id}/status` | Transition status (`APPROVED`, `SHIPPED`, `RECEIVED`) |
| `GET` | `/api/production-plans` | Assembly manufacturing schedules |
| `GET` | `/api/shortages` | Filtered detected shortages |
| `POST` | `/api/shortages/run-detection` | Trigger shortage detection algorithm |
| `GET` | `/api/shortages/{id}/mitigations` | Ranked mitigation recommendations |
| `POST` | `/api/mitigations/{id}/approve` | Approve and commit mitigation plan |
| `POST` | `/api/mitigations/{id}/reject` | Reject mitigation plan with planner rationale |
| `POST` | `/api/validation/run` | Execute 15-point validation engine |
| `GET` | `/api/exceptions/scenarios-overview` | Ground Truth vs. live system behavior comparison |
| `GET` | `/api/exports/csv` | Download CSV table export |

---

## 14. Export Functionality

Run the export script to generate all file formats:
```bash
python scripts/export_data.py --dir data/exports
```
Generates:
- **CSV Tables:** `skus.csv`, `locations.csv`, `forecast_demands.csv`, `inventory_balances.csv`, `suppliers.csv`, `supplier_capacities.csv`, `lead_times.csv`, `purchase_orders.csv`, `shortages.csv`, `mitigation_options.csv`.
- **JSON Datasets:** Matching formatted JSON files.
- **SQL Seed Script:** `data/exports/seed_data.sql` with valid ANSI SQL INSERT statements.
- **Ground Truth:** `data/ground_truth/ground_truth.csv` and `ground_truth.json`.
- **Dataset Manifest:** `data/manifests/manifest.json` detailing generation configuration, row counts, and source provenance.

---

## 15. Project Limitations & Future Enhancements

### Current Limitations:
- The synthetic dataset generates deterministic scenarios based on fixed seeds rather than live ERP streaming (SAP/NetSuite).
- Linear optimization solver (Simplex/MILP) is approximated via a deterministic multi-criteria scoring function.
- Weather and geopolitics delays are represented as logged integer delay days rather than probabilistic live AIS vessel tracking.

### Future Improvements:
- **MILP Optimization:** Integration of PuLP or SciPy Linear Programming for global cost-minimization supply network optimization.
- **ML Demand Forecasting:** Integration of Prophet / ARIMA models for self-learning demand projections from historical consumption.
- **Webhooks & Streaming:** Real-time Kafka event streaming for barcode scanning and warehouse receipt triggers.

---

## 16. Publishing to GitHub

To push this codebase to a public GitHub repository:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Add all files
git add .

# 3. Commit
git commit -m "feat: complete end-to-end inventory & supply chain demand planning system"

# 4. Set main branch
git branch -M main

# 5. Link to your GitHub remote repository
git remote add origin https://github.com/<your-username>/inventory-supply-chain.git

# 6. Push to GitHub
git push -u origin main
```

---

## License
MIT License. Developed for enterprise supply chain evaluation and technical demand planning.
