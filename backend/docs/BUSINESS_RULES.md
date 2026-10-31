# Supply Chain Planning Business Rules & Calculation Engine

## 1. Inventory Balancing & Reconciliation

### Weekly Balance Formula
For any SKU $s$ at Location $l$ in Week $w$:
$$\text{Closing Stock}_w = \text{Opening Stock}_w + \text{Received Stock}_w - \text{Demand}_w - \text{Adjustments}_w$$

### Temporal Propagation
The opening balance for the subsequent week is strictly anchored to the prior week's closing balance:
$$\text{Opening Stock}_{w+1} = \text{Closing Stock}_w$$

### Available Stock vs. Reserved Stock
Physical stock on hand is partitioned between unallocated and committed quantities:
$$\text{Available Stock}_w = \max(0, \text{Opening Stock}_w + \text{Received Stock}_w - \text{Reserved Stock}_w)$$

---

## 2. Projected Available Balance (PAB) & Time-Phased Logic

Projected Available Balance across horizon week $w \in [1, W]$:
$$\text{PAB}_w = \text{Opening Available}_w + \text{Confirmed Inbound POs}_w + \text{Inbound Transfers}_w + \text{Planned Production Receipts}_w - \text{Forecast Demand}_w$$

### Inbound Criteria:
- A purchase order is counted if and only if its effective arrival date ($\text{expected\_delivery\_date} + \text{transport\_delay\_days}$) lands within week $w$.
- Only valid statuses (`APPROVED`, `SHIPPED`, or `RECEIVED`) are credited. `CANCELLED` orders are excluded.
- Controlled deduplication: Each transaction reference is verified against `event_histories` and `inventory_transactions`. If duplicate receipt reference occurs, it is blocked and reported.

---

## 3. Shortage Detection & Root-Cause Attribution

### Shortage Trigger:
A shortage is flagged whenever:
$$\text{PAB}_w < 0$$
$$\text{Shortage Quantity} = |\text{PAB}_w|$$

### Root Cause Classification:
1. **DEMAND_SPIKE**: Demand in week $w > 1.8 \times$ historical mean demand for the SKU.
2. **DELAYED_SHIPMENT**: Inbound PO or transfer with arrival originally scheduled for week $w$ was delayed due to recorded `transport_delays`.
3. **SUPPLIER_CAPACITY_CONSTRAINT**: Inbound order was truncated or prevented because supplier reached $100\%$ capacity allocation.
4. **PRODUCTION_CAPACITY_CONSTRAINT**: Manufacturing plant hours were maxed out or component stock was inadequate.
5. **MISSING_LEAD_TIME**: Vendor or route lacks active lead-time data, preventing scheduled procurement.
6. **INSUFFICIENT_OPENING_INVENTORY**: Default attribution when baseline demand exceeds opening safety buffer without external disruptions.

### Severity Scoring:
- **CRITICAL**: Shortage quantity $\ge 70\%$ of forecast demand.
- **HIGH**: Shortage quantity between $35\%$ and $70\%$ of forecast demand.
- **MEDIUM**: Shortage quantity between $15\%$ and $35\%$ of forecast demand.
- **LOW**: Shortage quantity $< 15\%$ of forecast demand.

---

## 4. Mitigation Recommendation & Ranking Engine

For each shortage, the engine analyzes four strategies:

### Strategy 1: Supplier Purchase
- **Feasibility Conditions**:
  - Supplier is `ACTIVE`.
  - Active contract exists in `lead_times`.
  - Order quantity meets `min_order_quantity` ($\text{qty} = \max(\text{shortage\_quantity}, \text{MOQ})$).
  - Supplier has unallocated capacity: $\text{qty} \le \text{available\_capacity}$.
  - Expected delivery ($\text{now} + \text{lead\_time} + \text{delay}$) arrives $\le \text{shortage\_date}$.
- **Rejection Reason**: If capacity exceeded or lead time causes stock to arrive after shortage date.

### Strategy 2: Warehouse Stock Transfer
- **Feasibility Conditions**:
  - Source location $l_{src} \ne l_{dest}$.
  - Source location has excess available inventory above safety stock: $\text{available}_{l_{src}} - \text{safety\_stock}_{l_{src}} \ge \text{shortage\_quantity}$.
  - Transfer transit time arrives on or before shortage date.
- **Rejection Reason**: "Insufficient source warehouse surplus stock" or "Transit duration exceeds deadline".

### Strategy 3: Additional Production
- **Feasibility Conditions**:
  - SKU has an active Bill of Materials (`BOM_Header`).
  - Plant location has available hours: $(\text{shortage\_quantity} / \text{units\_per\_hour}) \le \text{available\_hours}$.
  - All component SKUs specified in `bom_components` have sufficient available inventory in the plant.
  - Production lead time finishes before shortage date.
- **Rejection Reason**: "BOM component stock shortage" or "Production capacity exceeded".

### Strategy 4: Approved Substitute SKU
- **Feasibility Conditions**:
  - An entry exists in `sku_substitutes` where `approval_status == 'APPROVED'`.
  - Current date is between `effective_from` and `effective_to`.
  - Substitute SKU has available on-hand stock $\ge (\text{shortage\_quantity} \times \text{conversion\_rate})$.
- **Rejection Reason**: "Substitute candidate is UNAPPROVED" (triggers Exception Scenario 2) or "Substitute lacks available stock".

### Recommendation Score Formulation:
For feasible options:
$$\text{Score} = w_{cs} \cdot S_{cs} + w_{cost} \cdot S_{cost} + w_{lead} \cdot S_{lead} - w_{risk} \cdot S_{risk}$$
Where:
- $S_{cs} \in [0, 100]$: Customer Service score (100 for zero customer impact).
- $S_{cost} \in [0, 100]$: Normalized cost efficiency relative to standard SKU cost.
- $S_{lead} \in [0, 100]$: Lead-time buffer ($100$ if arriving well ahead of shortage date).
- $S_{risk} \in [0, 100]$: Penalty based on supplier reliability or transfer distance.
- Weights: $w_{cs} = 0.40, w_{cost} = 0.25, w_{lead} = 0.25, w_{risk} = 0.10$.

Infeasible options receive Score = 0.00 and are ranked at the bottom with explicit rejection explanations.

---

## 5. Five Required Exception Scenarios

1. **Scenario 1: Inbound Counted Twice**
   - Inject a duplicate PO delivery receipt with identical tracking/reference.
   - Validation & Balance engine must detect duplicate reference in `inventory_transactions` and prevent balance inflation.

2. **Scenario 2: Substitute Not Approved**
   - Inject substitution request for an alternate SKU flagged `UNAPPROVED` in `sku_substitutes`.
   - Mitigation engine must reject option and record `DataQualityIssue`.

3. **Scenario 3: Supplier Capacity Exceeded**
   - Create purchase demand exceeding `available_capacity` in `supplier_capacities`.
   - Engine must reject or flag capacity violation.

4. **Scenario 4: Shortage Calculated Without Lead Time**
   - Nullify or remove lead-time record for a SKU-supplier-location lane.
   - Engine must block mitigation option, flag `MISSING_LEAD_TIME`, and never assume zero days.

5. **Scenario 5: Units of Measure Mismatch**
   - Attempt inbound delivery or substitution where UOM differs (e.g. PALLET vs UNITS) without an active conversion rule.
   - Engine must halt arithmetic addition, flag UOM mismatch issue, or apply approved factor from `uom_conversions`.
