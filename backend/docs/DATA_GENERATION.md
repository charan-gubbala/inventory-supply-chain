# Synthetic Data Generation Specification

## 1. Engine Architecture & Determinism

The synthetic data generation engine is built using Python 3.12+, Pandas, NumPy, and Faker with a fixed pseudo-random seed:
$$\text{SEED} = 20261022$$

Every generated identifier is strictly deterministic and zero-padded according to standard conventions:
- SKU: `SKU-000001`
- Location: `LOC-000001`
- Supplier: `SUP-000001`
- Demand: `DEM-SKU-000001-LOC-000001-2026W01`
- Purchase Order: `PO-2026-000001`
- Production Plan: `PROD-2026-000001`
- Shortage: `SHORT-2026-000001`
- Mitigation: `MIT-SHORT-2026-000001-01`

---

## 2. Operating Modes

### Starter Mode (`--mode starter`)
- 10 SKUs across 4 industrial categories.
- 3 Locations (1 Plant, 2 Distribution Centers).
- 5 Suppliers with diverse reliability tiers.
- 4 Weeks of planning horizon (`2026W01` through `2026W04`).
- 30 Inbound Purchase Orders.
- Fast execution for local testing, rapid CI/CD runs, and frontend development.

### Full Mode (`--mode full`)
- 3,000 SKUs.
- 50 Locations.
- 500 Suppliers.
- 52 Weeks of demand ($3,000 \times 50 \times 52 = 7,800,000$ demand combinations or configured sparse active lanes).
- 10,000 Inbound Purchase Orders.
- Employs chunked generator processing and bulk database streaming (`chunk_size=10000`) to guarantee execution within memory constraints.

---

## 3. Realistic Statistical Distributions

- **Product Categories**: Electronics ($30\%$), Apparel ($25\%$), Industrial Machinery ($20\%$), Pharmaceuticals ($15\%$), Packaging ($10\%$).
- **Demand Profiling**:
  - Baseline: Normal distribution $\mathcal{N}(\mu=200, \sigma=40)$
  - Seasonal: Sinusoidal modulation $A \sin(\frac{2\pi w}{52}) + \text{noise}$
  - Spikes: Poisson arrival process with multiplier $2.5 \times$ baseline
- **Supplier Lead Times**: Log-normal distribution with median between 5 and 28 days depending on category.
- **Exceptions Injected**:
  - Duplicate inbound events (Scenario 1)
  - Unapproved substitute links (Scenario 2)
  - Capacity boundary breaches (Scenario 3)
  - Missing lead time lane records (Scenario 4)
  - Incompatible unit of measure delivery (Scenario 5)
- **Ground Truth Output**: Stored in `data/ground_truth/ground_truth.csv` and `data/ground_truth/ground_truth.json`.
