# Market Basket Sentiment Clearance Optimizer 🛍️📈

> **Supply Chain Analytics, Market Basket Association Rules (Apriori), 3-Step NLP Review Diagnostics, and Gross Margin Recovery (GMROI)**

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)
![Framework](https://img.shields.io/badge/Framework-Streamlit%20%7C%20Apriori%20%7C%20VADER%20%7C%20TF--IDF-orange)
![License](https://img.shields.io/badge/License-MIT-green)

Inspired by retail operations (Zara, Amazon, H&M), this platform prevents margin destruction caused by flat 50%+ end-of-season clearance markdowns. By combining **Pareto ABC Inventory Classification**, **Gross Margin Return on Inventory (GMROI)**, **3-Step NLP Review Diagnostics (VADER + TF-IDF N-grams)**, and **Apriori Market Basket Association Rules**, the engine pairs slow-moving stock with high-demand anchor products to maximize gross margin dollars.

---

## 🔬 3-Step NLP Analytical Diagnostics Workflow

To connect unstructured customer feedback directly with merchandising actions, the project implements a structured 3-step NLP analytical pipeline:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Preprocessing & VADER Sentiment Polarity Scoring                              │
│ - Quantifies overall text polarity (Compound Score: -1.0 to +1.0)                      │
│ - Categorizes reviews into Positive, Negative, and Neutral                             │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Traditional NLP Feature Extraction (TF-IDF & N-Grams)                           │
│ - Extracts bi-grams & tri-grams (e.g., "runs small", "paper thin", "overpriced quality") │
│ - Answers the "WHY" behind negative VADER scores                                       │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
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

## 🎯 Business Problem & Solution Architecture

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

## 📁 Repository Structure

```
retail-basket-markdown-intelligence/
├── README.md                           # Comprehensive portfolio presentation & setup guide
├── requirements.txt                    # Project dependencies
├── config/
│   └── settings.yaml                   # Threshold configs (GMROI target, Apriori support/lift)
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

## 📊 Real Datasets Used

1. **[UCI Machine Learning Repository — Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail)**: 541,909 real line-item transactions from a UK online retailer (`InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`).
2. **[Women's Clothing E-Commerce Reviews Dataset](https://www.kaggle.com/datasets/nicapotato/womens-clothing-ecommerce-reviews)**: Real customer text reviews with star ratings, recommended status, and NLP text commentary.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Interactive Streamlit Dashboard
```bash
streamlit run app/streamlit_app.py
```

### 3. Generate Executive Presentation Deck (.pptx)
```bash
python3 reports/generate_deck.py
```

---

## 📜 License
Licensed under the [MIT License](LICENSE).
