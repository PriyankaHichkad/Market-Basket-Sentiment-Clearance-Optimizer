import os
import sys
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add src to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl_pipeline import ETLPipeline
from src.inventory_finance import InventoryFinanceAnalytics
from src.sentiment_diagnostics import SentimentDiagnostics
from src.market_basket import MarketBasketAnalyzer
from src.dynamic_bundling_engine import DynamicBundlingEngine

st.set_page_config(
    page_title="Market Basket Sentiment Clearance Optimizer",
    page_icon="🛍️",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 32px; font-weight: bold; color: #102542; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #0072CE; margin-bottom: 25px; }
    .metric-card { background-color: #F5F7FA; border-left: 5px solid #0072CE; padding: 15px; border-radius: 5px; }
    .metric-label { font-size: 13px; color: #555555; text-transform: uppercase; font-weight: bold; }
    .metric-val { font-size: 24px; font-weight: bold; color: #102542; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛍️ Market Basket Sentiment Clearance Optimizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Retail Merchandising Control Tower | Margin Recovery via Apriori Bundling & 3-Step NLP Review Diagnostics</div>', unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    raw_dir = os.path.join(project_dir, "data", "raw")
    
    etl = ETLPipeline(raw_dir)
    try:
        r_df, rev_df = etl.load_raw_data()
        clean_retail = etl.clean_retail_data(r_df)
        sku_df = etl.aggregate_sku_level_metrics(clean_retail)
        clean_reviews = etl.clean_reviews_data(rev_df)
    except Exception as e:
        st.error(f"Error loading datasets: {e}")
        return None, None, None, None, None
        
    # Financial Analytics
    ifa = InventoryFinanceAnalytics()
    sku_abc = ifa.calculate_abc_classification(sku_df)
    sku_fin = ifa.calculate_gmroi(sku_abc)
    
    # 3-Step NLP Sentiment Diagnostics
    sd = SentimentDiagnostics()
    step1_reviews = sd.step1_vader_preprocessing(clean_reviews)
    step2_ngrams = sd.step2_tfidf_ngram_extraction(step1_reviews)
    step3_sku_sentiment = sd.step3_aggregate_business_insights(step1_reviews)
    
    # Market Basket
    mba = MarketBasketAnalyzer(min_support=0.003, min_confidence=0.10, min_lift=1.1)
    b_matrix = mba.prepare_basket_matrix(clean_retail, max_items=100)
    freq_items = mba.run_apriori(b_matrix)
    rules = mba.generate_association_rules(freq_items)
    bundles = mba.find_bundle_recommendations(rules, sku_fin)
    
    return sku_fin, step1_reviews, step2_ngrams, step3_sku_sentiment, bundles

with st.spinner("Loading real-world e-commerce datasets and running 3-step NLP analytics engine..."):
    sku_df, reviews_df, ngrams_df, sku_sentiment_df, bundles_df = load_and_process_data()

if sku_df is None or sku_df.empty:
    st.error("Dataset load failed. Please ensure raw CSV files are downloaded in data/raw/")
    st.stop()

# Sidebar
st.sidebar.header("📊 Executive Scenario Controls")
abc_filter = st.sidebar.multiselect("ABC Classification Filter", options=sku_df['abc_class'].unique(), default=sku_df['abc_class'].unique())
bundle_discount_slider = st.sidebar.slider("Smart Bundle Discount (%)", min_value=10, max_value=40, value=20, step=5) / 100.0

df_filtered = sku_df[sku_df['abc_class'].isin(abc_filter)]

# KPI Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Total SKUs Analyzed</div><div class="metric-val">{len(df_filtered):,}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Average GMROI Index</div><div class="metric-val">{df_filtered["gmroi"].mean():.2f}x</div></div>', unsafe_allow_html=True)
with col3:
    c_stock_capital = df_filtered[df_filtered['abc_class'].str.startswith('C')]['avg_inventory_capital'].sum()
    st.markdown(f'<div class="metric-card"><div class="metric-label">Slow-Mover Stock Capital</div><div class="metric-val">${c_stock_capital:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    dead_stock_count = len(df_filtered[df_filtered['inventory_status'].str.contains('Dead Stock')])
    st.markdown(f'<div class="metric-card"><div class="metric-label">High Risk Dead Stock SKUs</div><div class="metric-val" style="color: #D9534F;">{dead_stock_count}</div></div>', unsafe_allow_html=True)

st.write("---")

# Main Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Inventory Health & GMROI Matrix",
    "💬 3-Step NLP Sentiment Diagnostics Workflow",
    "🏷️ Market Basket Bundles & Markdown Simulator",
    "📋 Strategic Deck & Executive Roadmap"
])

# Tab 1: Inventory Health & GMROI Matrix
with tab1:
    st.subheader("Inventory Ageing vs. Gross Margin Return on Inventory (GMROI)")
    fig_scatter = px.scatter(
        df_filtered,
        x="inventory_age_days",
        y="gmroi",
        color="abc_class",
        size="stock_on_hand",
        hover_data=["ProductID", "Description", "total_revenue", "inventory_status"],
        color_discrete_map={
            "A (High Velocity)": "#228B22",
            "B (Medium Velocity)": "#0072CE",
            "C (Slow Moving)": "#D9534F"
        },
        labels={"inventory_age_days": "Inventory Age (Days)", "gmroi": "GMROI Ratio ($ Gross Margin / $ Inventory Capital)"},
        title="Portfolio Matrix: Inventory Age vs GMROI Productivity"
    )
    fig_scatter.add_hline(y=1.2, line_dash="dash", line_color="orange", annotation_text="GMROI Alert Threshold (1.2x)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Top Slow-Moving SKUs at Risk of Dead Stock")
    st.dataframe(
        df_filtered[df_filtered['abc_class'].str.startswith('C')][
            ['ProductID', 'Description', 'abc_class', 'total_units_sold', 'total_revenue', 'stock_on_hand', 'inventory_age_days', 'gmroi', 'inventory_status']
        ].sort_values(by='gmroi', ascending=True).head(15),
        use_container_width=True
    )

# Tab 2: 3-Step NLP Sentiment Diagnostics Workflow
with tab2:
    st.subheader("💬 3-Step NLP Analytical Diagnostics Workflow")
    st.markdown("""
    This workflow bridges raw customer sentiment with operational merchandising decisions:
    1. **Step 1: VADER Polarity Scoring** (Quantifies overall positive vs negative tone).
    2. **Step 2: Traditional TF-IDF N-Gram Extraction** (Discovers bi-grams/tri-grams explaining *WHY* negative sentiment exists).
    3. **Step 3: Business Insights & SKU Category Aggregation** (Maps sentiment to product categories and markdown rules).
    """)
    
    st.write("---")
    
    # Step 1 Section
    st.markdown("### 🔹 Step 1: VADER Sentiment Polarity Scoring")
    if reviews_df is not None and not reviews_df.empty:
        col_s1_1, col_s1_2 = st.columns(2)
        with col_s1_1:
            sentiment_counts = reviews_df['sentiment_label'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment Label', 'Count']
            fig_pie = px.pie(sentiment_counts, names='Sentiment Label', values='Count', color='Sentiment Label',
                             color_discrete_map={'Positive': '#228B22', 'Negative': '#D9534F', 'Neutral': '#FFBF00'},
                             title="VADER Sentiment Proportions")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_s1_2:
            fig_hist = px.histogram(reviews_df, x="vader_compound", nbins=20, title="VADER Compound Score Distribution (-1.0 to +1.0)")
            st.plotly_chart(fig_hist, use_container_width=True)
            
        st.write("---")
        
        # Step 2 Section
        st.markdown("### 🔹 Step 2: Traditional NLP Feature Extraction (TF-IDF Bi-Grams & Tri-Grams)")
        st.caption("Extracted top recurring negative phrases using TF-IDF N-grams to answer 'WHY' reviews are negative.")
        if ngrams_df is not None and not ngrams_df.empty:
            fig_ngrams = px.bar(ngrams_df.head(10), x='tfidf_score', y='ngram_phrase', orientation='h',
                                color='tfidf_score', color_continuous_scale='Reds',
                                title="Top TF-IDF Negative Phrase Bi-Grams & Tri-Grams")
            fig_ngrams.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_ngrams, use_container_width=True)
        else:
            st.info("N-gram extraction complete.")

        st.write("---")
        
        # Step 3 Section
        st.markdown("### 🔹 Step 3: Business Insights & Category Aggregation")
        rc_counts = reviews_df['root_cause_category'].value_counts().reset_index()
        rc_counts.columns = ['Root Cause Category', 'Review Count']
        fig_rc = px.bar(rc_counts, x='Root Cause Category', y='Review Count', color='Root Cause Category',
                        title="Root Cause Breakdown (Sizing Flaw vs Price Resistance vs Quality Defect)")
        st.plotly_chart(fig_rc, use_container_width=True)
        
        st.subheader("Customer Review Text Inspector")
        sentiment_sub = st.selectbox("Filter Reviews by Sentiment", ["All", "Negative", "Positive", "Neutral"])
        if sentiment_sub != "All":
            sub_rev = reviews_df[reviews_df['sentiment_label'] == sentiment_sub]
        else:
            sub_rev = reviews_df
            
        disp_cols = [c for c in ['rating', 'vader_compound', 'sentiment_label', 'root_cause_category', 'clean_review'] if c in sub_rev.columns]
        st.dataframe(sub_rev[disp_cols].head(20), use_container_width=True)

# Tab 3: Market Basket Bundles & Markdown Simulator
with tab3:
    st.subheader("Discovered Co-Purchasing Bundles (Apriori Market Basket)")
    if bundles_df is not None and not bundles_df.empty:
        st.write(f"Mined **{len(bundles_df):,}** potential bundle combinations pairing Anchor SKUs with Slow-Movers.")
        st.dataframe(
            bundles_df[['anchor_sku', 'anchor_desc', 'anchor_class', 'slow_mover_sku', 'slow_mover_desc', 'slow_mover_class', 'support', 'confidence', 'lift']],
            use_container_width=True
        )
        
        st.subheader("⚡ Live Bundle Margin Recovery Simulator")
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            anc_select = st.selectbox("Select Anchor Product (High Velocity)", options=sku_df['ProductID'].head(50).unique(), index=0)
            anc_row = sku_df[sku_df['ProductID'] == anc_select].iloc[0]
            st.info(f"**Anchor SKU**: {anc_row['Description']}\n- Price: **${anc_row['avg_unit_price']:.2f}** | Cost: **${anc_row['avg_unit_cost']:.2f}** | Class: **{anc_row['abc_class']}**")
            
        with sim_col2:
            slow_select = st.selectbox("Select Slow Mover Product (C-Class)", options=sku_df[sku_df['abc_class'].str.startswith('C')]['ProductID'].unique(), index=0)
            slow_row = sku_df[sku_df['ProductID'] == slow_select].iloc[0]
            st.warning(f"**Slow Mover SKU**: {slow_row['Description']}\n- Price: **${slow_row['avg_unit_price']:.2f}** | Cost: **${slow_row['avg_unit_cost']:.2f}** | Stock: **{slow_row['stock_on_hand']} units**")
            
        dbe = DynamicBundlingEngine()
        sim_res = dbe.optimize_bundle_pricing(
            anchor_sku=str(anc_select),
            anchor_price=float(anc_row['avg_unit_price']),
            anchor_cost=float(anc_row['avg_unit_cost']),
            slow_sku=str(slow_select),
            slow_price=float(slow_row['avg_unit_price']),
            slow_cost=float(slow_row['avg_unit_cost']),
            bundle_discount_pct=bundle_discount_slider
        )
        
        st.write("#### Simulation Financial Comparison")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Combined Original Price", f"${sim_res['combined_original_price']:.2f}")
        c2.metric(f"Smart Bundle Price ({int(bundle_discount_slider*100)}% off)", f"${sim_res['bundle_price']:.2f}")
        c3.metric("Bundle Gross Margin ($)", f"${sim_res['bundle_gross_margin']:.2f}")
        c4.metric("Margin Dollars Saved vs Standalone 50% Slash", f"${sim_res['margin_saved_vs_clearance']:.2f}", delta=f"+${sim_res['margin_saved_vs_clearance']:.2f}")
        
    else:
        st.info("No association rules generated.")

# Tab 4: Strategic Deck & Executive Roadmap
with tab4:
    st.subheader("Strategic Recommendations & Execution Roadmap")
    st.markdown("""
    ### Merchandising & Supply Chain Execution Steps
    1. **Automate GMROI Triggers**: Configure ERP alerts for products reaching 45+ Days in Inventory with GMROI < 1.2x.
    2. **3-Step NLP Root-Cause Filtering**: Run VADER sentiment + TF-IDF N-grams on reviews. If negative sentiment is due to *Sizing/Fit*, stop price discounts and initiate vendor pattern corrections. If *Price Resistance*, approve bundle discounts.
    3. **Apriori Bundle Placement**: Push high-lift bundle recommendations directly to e-commerce product detail pages (PDP) as "Frequently Bought Together".
    4. **Dynamic Discount Allocation**: Apply 15-20% bundle discounts to maintain total gross margin dollars above product cost.
    """)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Market Basket Sentiment Clearance Optimizer**")
