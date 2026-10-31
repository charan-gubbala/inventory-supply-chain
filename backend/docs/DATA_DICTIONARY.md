# Data Dictionary: Inventory & Supply Chain Demand Planning System

## Overview
This document defines all entities, columns, data types, constraints, default values, units, nullability, relationships, and validation rules for the 11 core tables and supporting tables in the Inventory and Supply Chain Demand Planning System.

---

## 1. Core Entities

### 1.1 SKU (`skus`)
Master catalog of finished goods, raw materials, and components.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `sku_id` | Unique deterministic SKU identifier | VARCHAR(32) | Required | `SKU-[0-9]{6}` | - | Unique | Matches regex `^SKU-\d{6}$` | Primary Key |
| `name` | Commercial or material product name | VARCHAR(255) | Required | Non-empty string | - | Non-unique | Max 255 chars | - |
| `category` | Product hierarchy or family | VARCHAR(64) | Required | ELECTRONICS, APPAREL, INDUSTRIAL, PHARMA, PACKAGING | - | Non-unique | Must belong to valid category enum | - |
| `unit_of_measure` | Default operational unit of measure | VARCHAR(16) | Required | UNITS, BOX, PALLET, KG, LITER | - | Non-unique | Valid UOM enum | - |
| `cost_per_unit` | Standard unit production/purchase cost | NUMERIC(12, 2) | Required | >= 0.00 | USD | Non-unique | Must be non-negative | - |
| `price_per_unit` | Standard sales price per unit | NUMERIC(12, 2) | Required | >= cost_per_unit | USD | Non-unique | Must be >= cost_per_unit | - |
| `safety_stock_quantity` | Minimum safety buffer | INTEGER | Required | >= 0 | Units | Non-unique | Non-negative integer | - |
| `status` | Lifecycle status | VARCHAR(20) | Required | ACTIVE, INACTIVE, DISCONTINUED | - | Non-unique | Status enum | - |
| `created_at` | Record creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Record last modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.2 Location (`locations`)
Physical warehouses, distribution centers, and manufacturing plants.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `location_id` | Unique deterministic location identifier | VARCHAR(32) | Required | `LOC-[0-9]{6}` | - | Unique | Matches regex `^LOC-\d{6}$` | Primary Key |
| `name` | Facility name | VARCHAR(255) | Required | Non-empty string | - | Non-unique | Max 255 chars | - |
| `type` | Facility classification | VARCHAR(32) | Required | WAREHOUSE, DISTRIBUTION_CENTER, PLANT | - | Non-unique | Location type enum | - |
| `capacity_units` | Maximum physical storage capacity | INTEGER | Required | > 0 | Units | Non-unique | Strictly positive integer | - |
| `address` | Facility address / geography | VARCHAR(255) | Optional | String | - | Non-unique | Max 255 chars | - |
| `status` | Operational status | VARCHAR(20) | Required | ACTIVE, INACTIVE | - | Non-unique | Active/Inactive enum | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.3 ForecastDemand (`forecast_demands`)
Time-phased projected customer demand per SKU, location, and week.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `demand_id` | Deterministic demand identifier | VARCHAR(64) | Required | `DEM-{sku_id}-{location_id}-{iso_week}` | - | Unique | Deterministic composite string | Primary Key |
| `sku_id` | Foreign key referencing SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `location_id` | Foreign key referencing Location | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Must exist in `locations` | Foreign Key |
| `iso_week` | ISO week string | VARCHAR(8) | Required | `YYYYW[0-5][0-9]` e.g. `2026W01` | Week | Non-unique | Valid ISO week format | - |
| `forecast_quantity` | Quantity demanded | INTEGER | Required | >= 0 | Units | Non-unique | Non-negative integer | - |
| `demand_type` | Forecast demand driver | VARCHAR(32) | Required | BASELINE, PROMOTION, SEASONAL, SPIKE | - | Non-unique | DemandType enum | - |
| `forecast_date` | Date forecast was generated | DATE | Required | ISO Date `YYYY-MM-DD` | - | Non-unique | <= week start date | - |
| `confidence_level`| Statistical forecast confidence | NUMERIC(5, 2) | Optional | 0.00 - 100.00 | % | Non-unique | Between 0 and 100 | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.4 Inventory (`inventory_balances`)
Weekly snapshot and active stock levels for each SKU-location pairing.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `inventory_id` | Unique identifier | VARCHAR(64) | Required | `INV-{sku_id}-{location_id}-{iso_week}` | - | Unique | Composite unique ID | Primary Key |
| `sku_id` | Target SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `location_id` | Target Location | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Must exist in `locations` | Foreign Key |
| `iso_week` | Week of snapshot | VARCHAR(8) | Required | `YYYYWww` | Week | Non-unique | ISO week format | - |
| `opening_stock` | Beginning inventory balance | INTEGER | Required | Any integer | Units | Non-unique | Equal to previous week closing | - |
| `received_stock`| Stock received from inbound orders | INTEGER | Required | >= 0 | Units | Non-unique | Non-negative | - |
| `reserved_stock`| Allocated customer or transfer stock | INTEGER | Required | >= 0 | Units | Non-unique | Non-negative | - |
| `available_stock`| Stock immediately usable | INTEGER | Required | opening + received - reserved | Units | Non-unique | Reconciled balance | - |
| `incoming_stock`| In-transit POs & transfers expected | INTEGER | Required | >= 0 | Units | Non-unique | Non-negative | - |
| `adjustments` | Manual/scrap inventory adjustments | INTEGER | Required | Any integer | Units | Non-unique | Valid audit trail | - |
| `closing_stock` | Ending inventory balance | INTEGER | Required | opening + received - demand - adjustments | Units | Non-unique | Balanced formula | - |
| `projected_available_balance` | Time-phased projected balance | INTEGER | Required | available + incoming - demand | Units | Non-unique | Can be negative (shortage) | - |
| `unit_of_measure`| Unit of measure | VARCHAR(16) | Required | UNITS, BOX, PALLET, KG, LITER | - | Non-unique | Matches SKU or converted | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.5 Supplier (`suppliers`)
Commercial vendors providing raw materials, components, and finished products.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `supplier_id` | Unique deterministic supplier identifier | VARCHAR(32) | Required | `SUP-[0-9]{6}` | - | Unique | Matches regex `^SUP-\d{6}$` | Primary Key |
| `name` | Company or trading name | VARCHAR(255) | Required | Non-empty string | - | Non-unique | Max 255 chars | - |
| `rating` | Quality & reliability tier | NUMERIC(3, 2) | Required | 1.00 - 5.00 | Score | Non-unique | Between 1.00 and 5.00 | - |
| `on_time_delivery_rate` | Historical delivery reliability | NUMERIC(5, 2) | Required | 0.00 - 100.00 | % | Non-unique | Between 0 and 100 | - |
| `status` | Operational partnership status | VARCHAR(20) | Required | ACTIVE, INACTIVE, SUSPENDED | - | Non-unique | Supplier status enum | - |
| `contact_email` | Procurement contact email | VARCHAR(255) | Optional | Valid email format | - | Non-unique | Standard email regex | - |
| `address` | Headquarter or facility address | VARCHAR(255) | Optional | String | - | Non-unique | Max 255 chars | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.6 SupplierCapacity (`supplier_capacities`)
Weekly capacity limits per supplier and SKU.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `capacity_id` | Primary key identifier | VARCHAR(64) | Required | `CAP-{supplier_id}-{sku_id}-{effective_from}` | - | Unique | Composite unique ID | Primary Key |
| `supplier_id` | Referencing supplier | VARCHAR(32) | Required | Valid `suppliers.supplier_id` | - | Non-unique | Must exist in `suppliers` | Foreign Key |
| `sku_id` | Referencing SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `max_capacity_per_week` | Max supplier order fulfillment | INTEGER | Required | > 0 | Units/Wk | Non-unique | Strictly positive | - |
| `allocated_capacity` | Existing commitments this period | INTEGER | Required | >= 0 | Units/Wk | Non-unique | Non-negative | - |
| `available_capacity` | Remaining uncommitted capacity | INTEGER | Required | max_capacity - allocated | Units/Wk | Non-unique | >= 0 under valid state | - |
| `effective_from` | Effective start date | DATE | Required | ISO Date | - | Non-unique | <= `effective_to` | - |
| `effective_to` | Effective end date | DATE | Required | ISO Date | - | Non-unique | >= `effective_from` | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.7 LeadTime (`lead_times`)
Vendor lead-time, minimum order quantities, and unit pricing per SKU and delivery location.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `lead_time_id` | Unique lead time record identifier | VARCHAR(64) | Required | `LT-{supplier_id}-{sku_id}-{location_id}` | - | Unique | Composite ID | Primary Key |
| `supplier_id` | Referencing supplier | VARCHAR(32) | Required | Valid `suppliers.supplier_id` | - | Non-unique | Must exist in `suppliers` | Foreign Key |
| `sku_id` | Referencing SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `location_id` | Destination location | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Must exist in `locations` | Foreign Key |
| `base_lead_time_days` | Standard delivery lead time | INTEGER | Required | > 0 | Days | Non-unique | Non-zero, strictly positive | - |
| `min_order_quantity` | Minimum Order Quantity (MOQ) | INTEGER | Required | >= 1 | Units | Non-unique | Strictly positive | - |
| `cost_per_unit` | Contracted unit purchasing price | NUMERIC(12, 2) | Required | > 0.00 | USD | Non-unique | Strictly positive | - |
| `effective_from` | Contract effective start date | DATE | Required | ISO Date | - | Non-unique | <= `effective_to` | - |
| `effective_to` | Contract expiration date | DATE | Required | ISO Date | - | Non-unique | >= `effective_from` | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.8 PurchaseOrder (`purchase_orders`)
Inbound procurement orders placed with suppliers.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `po_id` | Unique deterministic PO identifier | VARCHAR(32) | Required | `PO-[0-9]{4}-[0-9]{6}` e.g. `PO-2026-000001` | - | Unique | Matches regex `^PO-\d{4}-\d{6}$` | Primary Key |
| `supplier_id` | Assigned supplier | VARCHAR(32) | Required | Valid `suppliers.supplier_id` | - | Non-unique | Supplier must be ACTIVE | Foreign Key |
| `sku_id` | Ordered SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `location_id` | Receiving destination facility | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Must exist in `locations` | Foreign Key |
| `order_quantity` | Units ordered | INTEGER | Required | >= MOQ | Units | Non-unique | Must satisfy supplier MOQ | - |
| `unit_cost` | Purchase price per unit | NUMERIC(12, 2) | Required | > 0.00 | USD | Non-unique | Strictly positive | - |
| `total_amount` | Total PO value | NUMERIC(14, 2) | Required | order_quantity * unit_cost | USD | Non-unique | Matches line items total | - |
| `order_date` | Date PO was placed | DATE | Required | ISO Date | - | Non-unique | <= `expected_delivery_date` | - |
| `expected_delivery_date`| Scheduled delivery date | DATE | Required | ISO Date | - | Non-unique | >= `order_date` + lead time | - |
| `actual_delivery_date` | Actual receiving date | DATE | Optional | ISO Date | - | Non-unique | Set only when RECEIVED | - |
| `status` | PO lifecycle status | VARCHAR(20) | Required | CREATED, APPROVED, SHIPPED, RECEIVED, CANCELLED | - | Non-unique | Follows sequential lifecycle | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.9 ProductionPlan (`production_plans`)
Internal manufacturing schedules for finished goods assembly or component conversion.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `plan_id` | Unique deterministic plan identifier | VARCHAR(32) | Required | `PROD-[0-9]{4}-[0-9]{6}` e.g. `PROD-2026-000001` | - | Unique | Matches regex `^PROD-\d{4}-\d{6}$` | Primary Key |
| `sku_id` | Manufactured SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must have valid BOM | Foreign Key |
| `location_id` | Manufacturing plant | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Facility must be PLANT type | Foreign Key |
| `iso_week` | Scheduled production week | VARCHAR(8) | Required | `YYYYWww` | Week | Non-unique | Valid ISO week | - |
| `planned_quantity` | Quantity scheduled | INTEGER | Required | > 0 | Units | Non-unique | Must respect plant capacity | - |
| `produced_quantity` | Actual finished output | INTEGER | Required | >= 0 | Units | Non-unique | Default 0 until finished | - |
| `status` | Production lifecycle status | VARCHAR(20) | Required | PLANNED, IN_PROGRESS, COMPLETED, CANCELLED | - | Non-unique | Valid ProductionStatus enum | - |
| `start_date` | Scheduled start date | DATE | Required | ISO Date | - | Non-unique | <= `end_date` | - |
| `end_date` | Scheduled completion date | DATE | Required | ISO Date | - | Non-unique | >= `start_date` | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.10 Shortage (`shortages`)
Detected deficits where projected available balance drops below zero.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `shortage_id` | Deterministic shortage identifier | VARCHAR(32) | Required | `SHORT-[0-9]{4}-[0-9]{6}` | - | Unique | Matches regex `^SHORT-\d{4}-\d{6}$` | Primary Key |
| `sku_id` | Shortage SKU | VARCHAR(32) | Required | Valid `skus.sku_id` | - | Non-unique | Must exist in `skus` | Foreign Key |
| `location_id` | Deficit location | VARCHAR(32) | Required | Valid `locations.location_id` | - | Non-unique | Must exist in `locations` | Foreign Key |
| `iso_week` | Week deficit occurs | VARCHAR(8) | Required | `YYYYWww` | Week | Non-unique | ISO week format | - |
| `shortage_quantity` | Unmet quantity | INTEGER | Required | > 0 | Units | Non-unique | Must equal abs(projected balance) | - |
| `expected_shortage_date`| First date of shortage impact | DATE | Required | ISO Date | - | Non-unique | Falls within `iso_week` | - |
| `root_cause` | Supply chain driver | VARCHAR(64) | Required | INSUFFICIENT_OPENING_INVENTORY, DEMAND_SPIKE, SUPPLIER_CAPACITY_CONSTRAINT, DELAYED_SHIPMENT, PRODUCTION_CAPACITY_CONSTRAINT, MISSING_LEAD_TIME | - | Non-unique | Explainable classification | - |
| `severity` | Business criticality | VARCHAR(16) | Required | LOW, MEDIUM, HIGH, CRITICAL | - | Non-unique | Defined by ratio of shortage to demand | - |
| `detection_date` | Timestamp when engine detected | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `status` | Remediation lifecycle status | VARCHAR(20) | Required | DETECTED, MITIGATED, RESOLVED, UNRESOLVED | - | Non-unique | Valid lifecycle state | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

### 1.11 MitigationOption (`mitigation_options`)
Recommended remediation actions ranked by cost, feasibility, lead time, and service level.

| Field Name | Description | Data Type | Req/Opt | Allowed Values / Format | Units | Uniqueness | Validation Rules | Key Status |
|------------|-------------|-----------|---------|-------------------------|-------|------------|------------------|------------|
| `mitigation_id` | Deterministic mitigation identifier | VARCHAR(48) | Required | `MIT-SHORT-[0-9]{4}-[0-9]{6}-[0-9]{2}` | - | Unique | Sequential index per shortage | Primary Key |
| `shortage_id` | Referencing shortage | VARCHAR(32) | Required | Valid `shortages.shortage_id` | - | Non-unique | Must exist in `shortages` | Foreign Key |
| `strategy_type` | Action strategy | VARCHAR(32) | Required | SUPPLIER_PURCHASE, WAREHOUSE_TRANSFER, ADDITIONAL_PRODUCTION, APPROVED_SUBSTITUTE | - | Non-unique | Valid MitigationStrategy enum | - |
| `proposed_quantity`| Proposed replenishment quantity | INTEGER | Required | >= shortage_quantity or MOQ | Units | Non-unique | Meets shortage / MOQ requirements | - |
| `estimated_cost` | Total estimated cost | NUMERIC(12, 2) | Required | >= 0.00 | USD | Non-unique | Unit cost * quantity + freight/prep | - |
| `expected_arrival_date`| Projected arrival date | DATE | Required | ISO Date | - | Non-unique | Calculated via lead time & delays | - |
| `source_supplier_id`| Source vendor if purchase | VARCHAR(32) | Optional | Valid `suppliers.supplier_id` | - | Non-unique | Required if SUPPLIER_PURCHASE | Foreign Key |
| `source_location_id`| Source facility if transfer | VARCHAR(32) | Optional | Valid `locations.location_id` | - | Non-unique | Required if WAREHOUSE_TRANSFER | Foreign Key |
| `substitute_sku_id`| Substitute SKU if substitution | VARCHAR(32) | Optional | Valid `skus.sku_id` | - | Non-unique | Required if APPROVED_SUBSTITUTE | Foreign Key |
| `capacity_available`| Whether capacity suffices | BOOLEAN | Required | TRUE, FALSE | - | Non-unique | Evaluated against limits | - |
| `is_feasible` | Feasible before shortage date | BOOLEAN | Required | TRUE, FALSE | - | Non-unique | arrival <= shortage date & capacity | - |
| `customer_service_impact`| Customer delivery impact | VARCHAR(16) | Required | HIGH, MEDIUM, LOW | - | Non-unique | Service impact enum | - |
| `risk_level` | Execution risk | VARCHAR(16) | Required | LOW, MEDIUM, HIGH | - | Non-unique | Risk enum | - |
| `recommendation_score`| Weighted ranking score | NUMERIC(6, 2) | Required | 0.00 - 100.00 | Points | Non-unique | Composite objective function score | - |
| `rank` | Prioritized ordinal rank | INTEGER | Required | >= 1 | Ordinal | Non-unique | Ordered by recommendation_score DESC | - |
| `approval_status` | User review status | VARCHAR(20) | Required | PROPOSED, APPROVED, REJECTED | - | Non-unique | Default PROPOSED | - |
| `rejection_reason` | Reason if rejected/infeasible | VARCHAR(255) | Optional | String | - | Non-unique | Required if is_feasible=FALSE | - |
| `explanation` | Natural language justification | TEXT | Required | Descriptive explanation | - | Non-unique | Transparent explanation of score | - |
| `created_at` | Creation timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |
| `updated_at` | Modification timestamp | TIMESTAMP | Required | ISO 8601 | - | Non-unique | Default CURRENT_TIMESTAMP | - |

---

## 2. Supporting Tables

### 2.1 SKU_Substitute (`sku_substitutes`)
Approved and unapproved alternative SKU relationships.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `substitute_id` | VARCHAR(64) | Required | Deterministic ID `SUB-{orig_sku}-{sub_sku}` | Primary Key |
| `original_sku_id` | VARCHAR(32) | Required | Primary SKU | Foreign Key -> `skus.sku_id` |
| `substitute_sku_id` | VARCHAR(32) | Required | Alternative candidate SKU | Foreign Key -> `skus.sku_id` |
| `approval_status` | VARCHAR(20) | Required | APPROVED, UNAPPROVED, PENDING | Enum |
| `conversion_rate` | NUMERIC(8, 4) | Required | Ratio (e.g. 1.0 = 1:1) | Default 1.0000 |
| `effective_from` | DATE | Required | Start date of approval | ISO Date |
| `effective_to` | DATE | Required | Expiration date of approval | ISO Date |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.2 BOM_Header (`bom_headers`)
Bill of Materials master record for assemblies.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `bom_id` | VARCHAR(32) | Required | Deterministic BOM identifier `BOM-{sku_id}-V1` | Primary Key |
| `finished_sku_id`| VARCHAR(32) | Required | Finished good SKU | Foreign Key -> `skus.sku_id` |
| `name` | VARCHAR(255) | Required | Bill of materials title | - |
| `version` | VARCHAR(16) | Required | BOM version (e.g. 1.0) | Default '1.0' |
| `effective_from` | DATE | Required | Effective start date | ISO Date |
| `effective_to` | DATE | Required | Effective end date | ISO Date |
| `is_active` | BOOLEAN | Required | Active status | Default TRUE |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.3 BOM_Component (`bom_components`)
Component lines required to assemble finished goods.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `component_id` | VARCHAR(64) | Required | Deterministic ID `BOMC-{bom_id}-{component_sku_id}` | Primary Key |
| `bom_id` | VARCHAR(32) | Required | Header reference | Foreign Key -> `bom_headers.bom_id` |
| `component_sku_id` | VARCHAR(32) | Required | Raw material / component SKU | Foreign Key -> `skus.sku_id` |
| `quantity_required` | NUMERIC(10, 4) | Required | Units required per 1 unit of finished good | > 0 |
| `unit_of_measure` | VARCHAR(16) | Required | Component UOM | Must match SKU or converted |
| `scrap_rate` | NUMERIC(5, 2) | Required | Expected scrap percentage (0-100) | Default 0.00 |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.4 ProductionCapacity (`production_capacities`)
Weekly manufacturing capacity limits per plant.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `prod_capacity_id` | VARCHAR(64) | Required | `PCAP-{location_id}-{iso_week}` | Primary Key |
| `location_id` | VARCHAR(32) | Required | Manufacturing plant | Foreign Key -> `locations.location_id` |
| `iso_week` | VARCHAR(8) | Required | ISO week | Format `YYYYWww` |
| `max_hours` | NUMERIC(8, 2) | Required | Total machine/labor hours available | > 0 |
| `allocated_hours` | NUMERIC(8, 2) | Required | Committed production hours | >= 0 |
| `available_hours` | NUMERIC(8, 2) | Required | Remaining hours | max_hours - allocated_hours |
| `units_per_hour` | NUMERIC(8, 2) | Required | Throughput rate | Default 10.00 |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.5 WarehouseTransfer (`warehouse_transfers`)
Inter-facility inventory movements.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `transfer_id` | VARCHAR(32) | Required | Deterministic ID `XFER-[0-9]{4}-[0-9]{6}` | Primary Key |
| `sku_id` | VARCHAR(32) | Required | SKU being moved | Foreign Key -> `skus.sku_id` |
| `from_location_id` | VARCHAR(32) | Required | Origin facility | Foreign Key -> `locations.location_id` |
| `to_location_id` | VARCHAR(32) | Required | Destination facility | Foreign Key -> `locations.location_id` |
| `quantity` | INTEGER | Required | Transfer units | > 0 |
| `lead_time_days` | INTEGER | Required | Transit duration | > 0 |
| `status` | VARCHAR(20) | Required | PLANNED, IN_TRANSIT, RECEIVED, CANCELLED | Enum |
| `ship_date` | DATE | Required | Ship departure date | ISO Date |
| `arrival_date` | DATE | Required | Arrival destination date | ISO Date |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.6 PurchaseOrderLine (`purchase_order_lines`)
Individual line items on purchase orders.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `po_line_id` | VARCHAR(48) | Required | `POL-{po_id}-{line_number}` | Primary Key |
| `po_id` | VARCHAR(32) | Required | Parent PO | Foreign Key -> `purchase_orders.po_id` |
| `line_number` | INTEGER | Required | Sequence index (1, 2, ...) | >= 1 |
| `sku_id` | VARCHAR(32) | Required | SKU ordered | Foreign Key -> `skus.sku_id` |
| `quantity` | INTEGER | Required | Ordered quantity | > 0 |
| `unit_price` | NUMERIC(12, 2) | Required | Price per unit | > 0 |
| `subtotal` | NUMERIC(14, 2) | Required | Line subtotal (qty * price) | > 0 |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.7 InventoryTransaction (`inventory_transactions`)
Auditable record of all stock adjustments, receipts, and issues.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `transaction_id` | VARCHAR(64) | Required | `TXN-[0-9]{4}-[0-9]{8}` | Primary Key |
| `sku_id` | VARCHAR(32) | Required | SKU reference | Foreign Key -> `skus.sku_id` |
| `location_id` | VARCHAR(32) | Required | Location reference | Foreign Key -> `locations.location_id` |
| `transaction_type`| VARCHAR(32) | Required | RECEIPT, SHIPMENT, ADJUSTMENT, RESERVATION, TRANSFER_OUT, TRANSFER_IN | Enum |
| `quantity` | INTEGER | Required | Signed or unsigned delta | Any non-zero integer |
| `reference_id` | VARCHAR(64) | Optional | Linking PO, SO, or Transfer ID | - |
| `transaction_date`| TIMESTAMP | Required | Execution timestamp | Default CURRENT_TIMESTAMP |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.8 Shipment (`shipments`) & TransportDelay (`transport_delays`)
Tracking physical goods in motion and en-route transit exceptions.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `shipment_id` | VARCHAR(32) | Required | `SHIP-[0-9]{4}-[0-9]{6}` | Primary Key |
| `po_id` | VARCHAR(32) | Optional | Associated PO | Foreign Key -> `purchase_orders.po_id` |
| `origin_type` | VARCHAR(20) | Required | SUPPLIER, WAREHOUSE | Enum |
| `origin_id` | VARCHAR(32) | Required | Supplier ID or Location ID | - |
| `destination_location_id`| VARCHAR(32)| Required | Destination facility | Foreign Key -> `locations.location_id` |
| `shipped_date` | DATE | Required | Actual departure date | ISO Date |
| `estimated_arrival_date` | DATE | Required | Scheduled arrival | ISO Date |
| `actual_arrival_date` | DATE | Optional | Actual arrival | ISO Date |
| `carrier` | VARCHAR(64) | Optional | Freight logistics provider | - |
| `tracking_number`| VARCHAR(64) | Optional | Carrier tracking number | - |
| `status` | VARCHAR(20) | Required | IN_TRANSIT, DELIVERED, DELAYED | Enum |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

`transport_delays`:
| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `delay_id` | VARCHAR(32) | Required | `DLY-[0-9]{4}-[0-9]{6}` | Primary Key |
| `shipment_id` | VARCHAR(32) | Required | Associated shipment | Foreign Key -> `shipments.shipment_id` |
| `delay_days` | INTEGER | Required | Additional delay in days | > 0 |
| `reason` | VARCHAR(255) | Required | Port congestion, customs, weather, breakdown | - |
| `reported_date` | DATE | Required | Date delay was registered | ISO Date |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.9 EventHistory (`event_histories`)
Immutable audit log tracking all domain events, transactions, and status transitions.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `event_id` | VARCHAR(64) | Required | `EVT-[0-9]{4}-[0-9]{8}` | Primary Key |
| `entity_type` | VARCHAR(32) | Required | PO, SHORTAGE, INVENTORY, MITIGATION | - |
| `entity_id` | VARCHAR(64) | Required | Foreign entity ID | - |
| `event_type` | VARCHAR(64) | Required | STATUS_CHANGE, SHORTAGE_DETECTED, RECONCILIATION | - |
| `payload` | JSON / TEXT | Required | State snapshot or structured delta | JSON format |
| `created_at` | TIMESTAMP | Required | Event timestamp | Default CURRENT_TIMESTAMP |

### 2.10 DataQualityIssue (`data_quality_issues`)
Recorded anomalies, validation errors, and controlled exception scenario outcomes.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `issue_id` | VARCHAR(64) | Required | `ISSUE-[0-9]{4}-[0-9]{6}` | Primary Key |
| `scenario_id` | VARCHAR(32) | Optional | SCENARIO-1 through SCENARIO-5 | Ground-truth reference |
| `issue_type` | VARCHAR(64) | Required | DUPLICATE_INBOUND, UNAPPROVED_SUBSTITUTE, CAPACITY_EXCEEDED, MISSING_LEAD_TIME, UOM_MISMATCH | - |
| `severity` | VARCHAR(16) | Required | INFO, WARNING, ERROR, CRITICAL | - |
| `affected_table` | VARCHAR(64) | Required | Table containing anomaly | - |
| `affected_record_id`| VARCHAR(64)| Required | Record ID of anomaly | - |
| `expected_outcome`| TEXT | Required | Expected system behavior | - |
| `actual_outcome` | TEXT | Required | Actual system behavior observed | - |
| `detection_status`| VARCHAR(20) | Required | DETECTED, UNDETECTED, RESOLVED | - |
| `details` | JSON / TEXT | Optional | Detailed diagnostic attributes | - |
| `created_at` | TIMESTAMP | Required | Detection timestamp | Default CURRENT_TIMESTAMP |

### 2.11 UnitOfMeasureConversion (`uom_conversions`)
Conversion rates between units of measure.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `conversion_id` | VARCHAR(32) | Required | `UOM-{from_uom}-{to_uom}` | Primary Key |
| `from_uom` | VARCHAR(16) | Required | Source unit (BOX, PALLET, KG, LITER, UNITS)| - |
| `to_uom` | VARCHAR(16) | Required | Target unit (UNITS, KG, etc.) | - |
| `factor` | NUMERIC(10, 4) | Required | Multiplier: target = source * factor | > 0 |
| `is_active` | BOOLEAN | Required | Active status | Default TRUE |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |

### 2.12 SKU_Location Bridge (`sku_locations`)
Configured parameters for a specific SKU stored at a specific facility.

| Field Name | Data Type | Req/Opt | Description | Keys & Constraints |
|------------|-----------|---------|-------------|--------------------|
| `id` | VARCHAR(64) | Required | `SKULOC-{sku_id}-{location_id}` | Primary Key |
| `sku_id` | VARCHAR(32) | Required | SKU reference | Foreign Key -> `skus.sku_id` |
| `location_id` | VARCHAR(32) | Required | Location reference | Foreign Key -> `locations.location_id` |
| `reorder_point` | INTEGER | Required | Inventory trigger level | >= 0 |
| `lead_time_days` | INTEGER | Required | Facility internal processing days | >= 0 |
| `safety_stock` | INTEGER | Required | Site-specific safety buffer | >= 0 |
| `created_at` | TIMESTAMP | Required | Creation timestamp | Default CURRENT_TIMESTAMP |
