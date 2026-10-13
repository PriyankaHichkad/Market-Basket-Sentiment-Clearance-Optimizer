import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np

from src.etl_pipeline import ETLPipeline
from src.inventory_finance import InventoryFinanceAnalytics
from src.sentiment_diagnostics import SentimentDiagnostics
from src.market_basket import MarketBasketAnalyzer
from src.dynamic_bundling_engine import DynamicBundlingEngine

def run_actual_analysis():
    print("=" * 60)
    print("EMPIRICAL FACT & METRICS AUDIT (NO HARDCODING)")
    print("=" * 60)
    
    # 1. ETL
    etl = ETLPipeline("data/raw")
    r_df, rev_df = etl.load_raw_data()
    raw_retail_count = len(r_df)
    raw_rev_count = len(rev_df)
    
    clean_r = etl.clean_retail_data(r_df)
    clean_retail_count = len(clean_r)
    unique_invoices = clean_r['InvoiceNo'].nunique()
    total_revenue = clean_r['LineRevenue'].sum()
    
    sku_df = etl.aggregate_sku_level_metrics(clean_r)
    total_skus = len(sku_df)
    
    clean_rev = etl.clean_reviews_data(rev_df)
    
    print("\n[ETL Pipeline Results]")
    print(f"Raw Retail Rows: {raw_retail_count:,}")
    print(f"Clean Retail Rows: {clean_retail_count:,}")
    print(f"Unique Invoices: {unique_invoices:,}")
    print(f"Total Revenue: ${total_revenue:,.2f}")
    print(f"Unique SKUs Aggregated: {total_skus:,}")
    print(f"Customer Reviews Ingested: {len(clean_rev):,}")
    
    # 2. Inventory Finance
    ifa = InventoryFinanceAnalytics()
    abc_df = ifa.calculate_abc_classification(sku_df)
    fin_df = ifa.calculate_gmroi(abc_df)
    
    a_skus = fin_df[fin_df['abc_class'].str.startswith('A')]
    b_skus = fin_df[fin_df['abc_class'].str.startswith('B')]
    c_skus = fin_df[fin_df['abc_class'].str.startswith('C')]
    
    dead_stock = fin_df[fin_df['inventory_status'].str.contains('Dead Stock')]
    total_inventory_cap = fin_df['avg_inventory_capital'].sum()
    c_cap = c_skus['avg_inventory_capital'].sum()
    dead_cap = dead_stock['avg_inventory_capital'].sum()
    
    print("\n[Pareto ABC & Financial Classification]")
    print(f"A-Class (High Velocity): {len(a_skus):,} SKUs ({len(a_skus)/total_skus*100:.1f}%) | ${a_skus['total_revenue'].sum():,.2f} ({a_skus['total_revenue'].sum()/total_revenue*100:.1f}% rev)")
    print(f"B-Class (Medium Velocity): {len(b_skus):,} SKUs ({len(b_skus)/total_skus*100:.1f}%) | ${b_skus['total_revenue'].sum():,.2f} ({b_skus['total_revenue'].sum()/total_revenue*100:.1f}% rev)")
    print(f"C-Class (Slow Moving): {len(c_skus):,} SKUs ({len(c_skus)/total_skus*100:.1f}%) | ${c_skus['total_revenue'].sum():,.2f} ({c_skus['total_revenue'].sum()/total_revenue*100:.1f}% rev)")
    print(f"Dead Stock (GMROI < 1.2 in C-Class): {len(dead_stock):,} SKUs")
    print(f"Total Inventory Capital Investment: ${total_inventory_cap:,.2f}")
    print(f"Capital in C-Class Slow Movers: ${c_cap:,.2f} ({c_cap/total_inventory_cap*100:.1f}%)")
    print(f"Capital in Dead Stock: ${dead_cap:,.2f} ({dead_cap/total_inventory_cap*100:.1f}%)")
    print(f"Average Portfolio GMROI: {fin_df['gmroi'].mean():.2f}x")
    print(f"Average C-Class GMROI: {c_skus['gmroi'].mean():.2f}x")
    
    # 3. NLP Diagnostics
    sd = SentimentDiagnostics()
    step1_rev = sd.step1_vader_preprocessing(clean_rev)
    pos_count = (step1_rev['sentiment_label'] == 'Positive').sum()
    neg_count = (step1_rev['sentiment_label'] == 'Negative').sum()
    neu_count = (step1_rev['sentiment_label'] == 'Neutral').sum()
    
    step2_ng = sd.step2_tfidf_ngram_extraction(step1_rev)
    step3_cats = step1_rev[step1_rev['sentiment_label'] == 'Negative']['root_cause_category'].value_counts()
    
    print("\n[3-Step NLP Review Diagnostics]")
    print(f"Total Reviews Scored: {len(step1_rev):,}")
    print(f"Positive Reviews: {pos_count:,} ({pos_count/len(step1_rev)*100:.1f}%)")
    print(f"Negative Reviews: {neg_count:,} ({neg_count/len(step1_rev)*100:.1f}%)")
    print(f"Neutral Reviews: {neu_count:,} ({neu_count/len(step1_rev)*100:.1f}%)")
    print(f"Top 5 N-Gram Root Cause Phrases:")
    for idx, r in step2_ng.head(5).iterrows():
        print(f"   - '{r['ngram_phrase']}': TF-IDF = {r['tfidf_score']:.3f}")
    print("Negative Reviews Root Cause Breakdown:")
    for cat, cnt in step3_cats.items():
        print(f"   - {cat}: {cnt:,} ({cnt/neg_count*100:.1f}%)")
        
    # 4. Apriori & Bundling
    mba = MarketBasketAnalyzer(min_support=0.005, min_confidence=0.05, min_lift=1.05)
    b_matrix = mba.prepare_basket_matrix(clean_r, sku_analytics_df=fin_df, max_items=100)
    freq_items = mba.run_apriori(b_matrix)
    rules = mba.generate_association_rules(freq_items)
    bundles = mba.find_bundle_recommendations(rules, fin_df)
    
    print("\n[Market Basket & Bundling Mining]")
    print(f"Frequent Itemsets: {len(freq_items):,}")
    print(f"Association Rules Generated: {len(rules):,}")
    print(f"Cross-Tier Bundle Pairs (Anchor + Slow Mover): {len(bundles):,}")
    if not bundles.empty:
        print(f"Bundle Support Range: {bundles['support'].min():.4f} - {bundles['support'].max():.4f}")
        print(f"Bundle Confidence Range: {bundles['confidence'].min():.2%} - {bundles['confidence'].max():.2%}")
        print(f"Bundle Lift Range: {bundles['lift'].min():.2f} - {bundles['lift'].max():.2f} (Avg: {bundles['lift'].mean():.2f})")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_actual_analysis()
