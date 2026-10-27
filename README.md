# Market Basket Sentiment Clearance Optimizer

> **Supply Chain Analytics, Market Basket Association Rules (Apriori), 3-Step NLP Review Diagnostics, and Gross Margin Recovery (GMROI)**

Inspired by retail operations (Zara, Amazon, H&M), this platform prevents margin destruction caused by flat 50%+ end-of-season clearance markdowns. By combining **Pareto ABC Inventory Classification**, **Gross Margin Return on Inventory (GMROI)**, **3-Step NLP Review Diagnostics (VADER + TF-IDF N-grams)**, and **Apriori Market Basket Association Rules**, the engine pairs slow-moving stock with high-demand anchor products to maximize gross margin dollars.

---

## Data Provenance & Financial Modeling Disclosure

To ensure complete transparency during technical review:

### 1. Observed Real-World Datasets
* **UCI Machine Learning Repository — Online Retail Transaction Dataset**: 541,909 real customer transaction logs from a UK online retailer (`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`).
* **Kaggle Women's Clothing E-Commerce Reviews Dataset**: 23,486 real customer text reviews with 10 variables (`Review Text`, `Rating`, `Recommended IND`, `Clothing ID`, `Department Name`, `Class Name`).

### 2. Modeled Supply Chain & Financial Assumptions
Public transaction logs contain retail selling prices and quantities, but omit wholesale unit costs and warehouse stock levels. To calculate financial metrics (**GMROI** and **ABC Pareto Velocity**), the pipeline models these fields based on standard retail supply chain principles:
* **Wholesale Unit Cost (`avg_unit_cost`)**: Modeled assuming a standard retail gross margin range of **40% to 60%** on average selling price (derived deterministically via `zlib.crc32(ProductID)`).
* **Stock On Hand (`stock_on_hand`) & Days of Supply (`days_of_supply`)**: Modeled from tier-based Days of Supply (DOS) targets (A-Class: 35–50 days, B-Class: 55–75 days, C-Class: 130–220+ days with aging penalty).

---

## 3-Step NLP Analytical Diagnostics Workflow

To connect unstructured customer feedback directly with merchandising actions, the project implements a structured 3-step NLP analytical pipeline running on 23,486 real Kaggle customer reviews:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Preprocessing & VADER Sentiment Polarity Scoring                              │
│ - Quantifies overall text polarity (Compound Score: -1.0 to +1.0)                      │
│ - Categorizes reviews into Positive, Negative, and Neutral                             │
└───────────────────────────┬────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Traditional NLP Feature Extraction (TF-IDF & N-Grams)                           │
│ - Extracts bi-grams & tri-grams (e.g., "runs small", "paper thin", "poor quality")      │
│ - Answers the "WHY" behind negative VADER scores across 1,300+ negative reviews        │
└───────────────────────────┬────────────────────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Business Insight & Category Aggregation                                        │
│ - Aggregates root causes by Product SKU & Department                                   │
│ - Distinguishes Sizing Flaws (Stop discount, fix pattern) from Price Resistance        │
│   (Approve 15-20% bundle discount) and Quality Defects (Vendor return)                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Business Problem & Solution Architecture

### The Retail Dilemma
Retailers accumulate stagnant, slow-moving C-Class inventory at season end. Standard operations slash prices by 50–70%, eroding gross margins below unit cost while ignoring the root cause of stagnation.

### Integrated Pipeline Architecture
```
                             ┌───────────────────────────────────────────────────────────┐
                             │               Real-World E-Commerce Datasets              │
                             │ (500k+ Online Retail Transactions | 23k+ Text Reviews)    │
                             └─────────────────────────────┬─────────────────────────────┘
                                                           │
                                                           ▼
                             ┌───────────────────────────────────────────────────────────┐
                             │                    Data ETL & Pipeline                    │
                             │   - SKU Velocity & Ageing    - Order Association Prep     │
                             └──────────────┬─────────────────────────────┬──────────────┘
                                            │                             │
                                            ▼                             ▼
┌──────────────────────────────────────────────────────┐   ┌──────────────────────────────────────────────────┐
│             Inventory & Financial Analytics          │   │           Market Basket & Sentiment AI           │
│ - ABC Classification (Velocity / Revenue)            │   │ - Apriori Co-purchasing Rules (Support/Lift)     │
│ - GMROI (Gross Margin Return on Inventory)           │   │ - VADER + TF-IDF N-Gram Text Diagnostics         │
│ - Holding Cost & Ageing Thresholds                   │   │ - Root-Cause Categorization (Price/Fit/Quality)  │
└───────────────────────────┬──────────────────────────┘   └────────────────────────┬─────────────────────────┘
                            │                                                       │
                            └───────────────────────────┬───────────────────────────┘
                                                        │
                                                        ▼
                             ┌───────────────────────────────────────────────────────────┐
                             │         Dynamic Markdown & Bundling Engine                │
                             │ - Pair Slow Movers (C-Class) with Anchor Products (A-Class)│
                             │ - Calculate Optimal Markdown Discount Tiers               │
                             │ - Profit Margin Protection & Inventory Recovery Estimate  │
                             └──────────────────────────┬────────────────────────────────┘
                                                        │
                                                        ▼
                                ┌─────────────────────────────────────────────────────┐
                                │             Deliverables & Outputs                  │
                                ├──────────────────────────┬──────────────────────────┤
                                │ 💻 Code & Interactive App│ 📊 Business Deck / PPT   │
                                │ - Modular Python Engine  │ - 10-Slide Exec Storyboard│
                                │ - Interactive Streamlit  │ - Automated PPTX Script │
                                │ - Power BI/Tableau Spec  │ - Strategy Recommendations│
                                └──────────────────────────┴──────────────────────────┘
```

---

## Resume Metrics Reproducibility & Audit Guide

Every metric on the submitted resume is 100% reproducible directly from the raw data using `python3 scripts/audit_metrics.py`. This section details the exact data sources, formulas, denominators, and methodology for each resume bullet.

| Resume Claim | Underlying Empirical Finding | Dataset & Methodology | Audit Verification Script |
|---|---|---|---|
| **Ranked 3,907 SKUs across 540K+ lines via Pareto ABC & GMROI, isolating 1,061 dead-stock clearance items.** | **541,909 raw rows** $\rightarrow$ **3,907 unique SKUs**; **1,061 dead-stock items** locking up **$151,900** in modeled capital. | **UCI Online Retail Dataset**: Aggregated transaction lines. Revenue ranked into Pareto tiers (Top 70% = A, Next 20% = B, Tail 10% = C with 2,574 SKUs). Dead stock defined as C-Class with modeled GMROI < 1.20x. | `python3 scripts/audit_metrics.py` (Section 1 & 2) |
| **Executed 3-step NLP pipeline with VADER, TF-IDF on 23K reviews, tracing 54% of negative feedback to sizing flaws.** | **23,486 total reviews** $\rightarrow$ **1,335 negative reviews**; **719 attributed to sizing/fit flaws** (**53.9%** $\approx$ **54%**). | **Kaggle Women's Clothing Reviews**: VADER polarity filters negative reviews (compound < -0.05). TF-IDF n-grams extracted ('runs large', 'runs small'). Keyword rule dictionary maps 719 / 1,335 negative reviews to Sizing & Fit. | `python3 scripts/audit_metrics.py` (Section 3) |
| **Applied Apriori association rules, surfacing 52 anchor and slow-mover clearance bundle pairs with 3.9x average lift.** | **52 cross-tier bundle pairs** mined with an **average Lift of 3.93x** (range: 2.01x – 6.73x). | **UCI Online Retail Baskets**: Apriori algorithm (`min_support=0.005`, `min_confidence=0.05`, `min_lift=1.05`) mined from transaction baskets, filtered for cross-tier pairs (A-Class Anchor + C-Class Slow Mover). | `python3 scripts/audit_metrics.py` (Section 4) |
| **Deployed Streamlit simulator comparing bundle margins to 50% markdown; proved 16 of 50 bundles accretive at 20%.** | **16 of 50 bundles accretive** in legacy baseline; **15 of 52 accretive** in merchandise-only per-unit mode; **41 of 52** (blanket) and **52 of 52** (targeted) beat markdown in clearance scenario. | **Dynamic Bundling Engine**: Compares bundle margin dollars against a 50% standalone markdown. Preserved as a reproducible benchmark in both legacy (unfiltered) and clean catalog evaluations. | `python3 scripts/audit_metrics.py` (Section 5 & 6) |

### Contextual Notes for Technical Reviewers

1. **Independent Benchmark Datasets**: 
   The platform integrates two real-world datasets to demonstrate complementary retail capabilities:
   * The **UCI Online Retail Dataset** (541K transaction rows) drives transaction basket mining, Pareto classification, and inventory velocity.
   * The **Women's Clothing E-Commerce Reviews Dataset** (23.5K reviews) is an independent customer feedback benchmark used to demonstrate unstructured NLP return diagnostics. The review text models general apparel return drivers and does not describe the giftware merchandise in the UCI transaction log.
2. **Modeled Financial Inputs vs. Realized Outcomes**:
   Public transaction logs record sales prices and quantities, but confidential wholesale costs and warehouse stock levels are not included in public datasets. Unit costs (modeled at 40–60% gross margin) and inventory levels (modeled from Days of Supply targets) are deterministic modeling assumptions, not realized accounting records.
3. **Per-Unit Margin vs. Sell-Through Clearance Scenarios**:
   * **Per-Unit View (16 of 50 / 15 of 52)**: Assumes equal 1:1 unit sales between bundling and markdown. Because the anchor is often priced higher than the slow mover, a blanket 20% discount on both items gives away anchor margin unless the anchor-to-slow price ratio is $\le 1.50$.
   * **Sell-Through Clearance Scenario (41 of 52 / 52 of 52)**: Evaluates total gross profit over a 45-day window where bundling achieves higher velocity (80% sell-through) than a markdown (60% sell-through), accounting for holding costs and anchor incrementality.

---

## Sell-Through Scenario Analysis (modeled assumptions)

The per-unit bundle comparison assumes the same number of units clear under every strategy. The reason to bundle is that it should clear **more** stock, so the scenario model (`DynamicBundlingEngine.simulate_clearance_scenario`) makes that an explicit input. It compares gross profit over a clearance window for a standalone 50% markdown versus a bundle, with unsold units carrying holding cost.

| Parameter | Baseline | Meaning |
|---|---|---|
| `markdown_sell_through` | 60% | Share of slow-mover stock a 50% markdown clears in the window |
| `bundle_sell_through` | 80% | Share cleared inside bundles in the same window |
| `anchor_incremental_share` | 30% | Share of bundled anchor units that are genuinely new sales; the rest would have sold at full price, so the bundle discount on them is given away |
| `bundle_discount_scope` | `both` | `both` discounts anchor + slow mover; `slow_only` keeps the anchor at list price |
| `window_days` | 45 | Clearance window; sets holding cost on unsold units |

**None of these are measured.** They are scenario inputs: the output answers "under these assumptions, does bundling beat a markdown?" and "how much sell-through would bundling need to break even?". Reproduce with `python3 scripts/scenario_analysis.py`, or adjust the sliders in the dashboard.

**Baseline result on the 52 mined bundles**

| Discount design | Bundles beating the 50% markdown | Median profit delta | Total modeled delta |
|---|---|---|---|
| Anchor + slow mover (20% off both) | 41 / 52 | +$77.63 | +$1,951 |
| Slow mover only (20% off, anchor at list) | 52 / 52 | +$343.25 | +$23,293 |

**What the sensitivity grid shows**

* Outcomes depend far more on anchor incrementality and the anchor-to-slow-mover price ratio than on sell-through. With a blanket discount, bundles beat the markdown in only 15 / 52 cases if none of the bundled anchor sales are incremental, and 52 / 52 if 60% are.
* Blanket bundle discounts lose when the anchor is priced well above the slow mover: bundles with an anchor more than 5x the slow-mover price won in 3 of 13, while bundles at 5x or less won in 38 of 39.
* Discounting only the slow mover beat the markdown in every cell of the sell-through x incrementality grid, and at every markdown depth tested (30%, 40%, 50%) under the baseline assumptions. This is close to structural: it is the same clearance item at a smaller discount, so it only loses if the bundle sells far fewer units than the markdown.

**Limitations to keep in mind when reading these numbers**

* Costs are modeled at a 40-60% margin, so a 50% markdown sells at or below cost for roughly half of the C-Class catalog, and for all 6 slow movers that appear in bundles. That makes the markdown a weak benchmark, and the dollar figures above should be read as a comparison under assumptions, not as recovered profit.
* The 52 bundles are 6 distinct slow-mover SKUs paired with 25 anchors; two of the slow movers account for 44 bundles.
* ABC tiers rank SKUs by revenue share, so a low-priced item that sells in volume can land in C-Class. The "dead stock" flag therefore means low revenue contribution plus low modeled GMROI, not zero sales (the flagged SKUs have a median of 142 units sold).
* Non-merchandise StockCodes (postage, carriage, fees, manual adjustments, gift vouchers) are excluded in the ETL. Left in, "DOTCOM POSTAGE" ranks as the top A-Class SKU and appears as a bundle anchor.

---

## Repository Structure

```
retail-basket-markdown-intelligence/
├── README.md                           # Comprehensive portfolio presentation & setup guide
├── requirements.txt                    # Project dependencies
├── config/
│   └── settings.yaml                   # Threshold configs (GMROI target, Apriori support/lift)
├── scripts/
│   ├── download_data.py                # Automated data download utility for fresh clones
│   ├── audit_metrics.py                # Recomputes every headline metric from the data
│   └── scenario_analysis.py            # Sell-through scenario grid on the mined bundles
├── data/
│   ├── raw/                            # Real-world raw e-commerce CSV datasets (Online Retail, Reviews)
│   └── processed/                      # Analytics-ready aggregated tables
├── src/
│   ├── etl_pipeline.py                 # Ingestion, cleaning, SKU velocity aggregation
│   ├── inventory_finance.py            # ABC Pareto classification & GMROI ratio calculation
│   ├── market_basket.py                # Apriori frequent itemsets & high-lift bundle rules
│   ├── sentiment_diagnostics.py        # 3-Step NLP Sentiment Engine (VADER + TF-IDF N-grams)
│   └── dynamic_bundling_engine.py      # Dynamic bundle pricing & margin recovery optimizer
├── app/
│   └── streamlit_app.py                # Interactive Web Control Tower & Live Simulator
└── reports/
    ├── generate_deck.py                # Python-PPTX script auto-generating 10-slide executive deck
    └── executive_presentation_deck.pptx# Executive presentation PowerPoint deck
```

---

## Quick Start Guide

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/PriyankaHichkad/Market-Basket-Sentiment-Clearance-Optimizer.git
cd Market-Basket-Sentiment-Clearance-Optimizer
pip install -r requirements.txt
```

### 2. Download Raw Datasets
```bash
python scripts/download_data.py
```
*(Note: The Streamlit app also features self-healing data downloading and will automatically fetch datasets if run directly).*

### 3. Launch Interactive Streamlit Dashboard
```bash
streamlit run app/streamlit_app.py
```

### 4. Generate Executive Presentation Deck (.pptx)
```bash
python3 reports/generate_deck.py
```

---

## Tools and Libraries Used

* **Python 3.11+**: https://www.python.org/
* **Streamlit**: https://streamlit.io/
* **mlxtend (Apriori Algorithm)**: https://rasbt.github.io/mlxtend/
* **vaderSentiment**: https://github.com/cjhutto/vaderSentiment
* **scikit-learn (TF-IDF Vectorizer)**: https://scikit-learn.org/
* **pandas**: https://pandas.pydata.org/
* **numpy**: https://numpy.org/
* **Plotly**: https://plotly.com/python/
* **python-pptx**: https://python-pptx.readthedocs.io/
