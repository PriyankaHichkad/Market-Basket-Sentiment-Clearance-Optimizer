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
* **Wholesale Unit Cost (`avg_unit_cost`)**: Modeled assuming a standard retail gross margin range of **40% to 60%** on average selling price.
* **Stock On Hand (`stock_on_hand`) & Inventory Age (`inventory_age_days`)**: Modeled based on observed sales velocity and transaction recency (slow-moving items modeled with higher sitting stock capital).

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

## Repository Structure

```
retail-basket-markdown-intelligence/
├── README.md                           # Comprehensive portfolio presentation & setup guide
├── requirements.txt                    # Project dependencies
├── config/
│   └── settings.yaml                   # Threshold configs (GMROI target, Apriori support/lift)
├── scripts/
│   └── download_data.py                # Automated data download utility for fresh clones
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
