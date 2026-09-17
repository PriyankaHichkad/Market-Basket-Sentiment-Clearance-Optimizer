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

# -------------------------------------------------------------
# PAGE CONFIGURATION & ENTERPRISE THEMING
# -------------------------------------------------------------
st.set_page_config(
    page_title="Market Basket & Sentiment Clearance Control Tower",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Styling
st.markdown("""
<style>
    /* Main Layout Styling */
    .stApp { background-color: #FAFAFA; }
    
    /* Header Styling */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-title { font-size: 28px; font-weight: 800; color: #FFFFFF; margin: 0; letter-spacing: -0.5px; }
    .hero-subtitle { font-size: 15px; color: #93C5FD; margin-top: 6px; font-weight: 400; }
    
    /* KPI Metric Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .kpi-label { font-size: 12px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 26px; font-weight: 800; color: #0F172A; margin-top: 4px; }
    .kpi-subtext { font-size: 12px; color: #10B981; margin-top: 4px; font-weight: 600; }
    .kpi-alert { color: #EF4444 !important; }
    
    /* Section Cards */
    .content-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }
    
    /* Executive Badges */
    .badge-a { background-color: #D1FAE5; color: #065F46; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
    .badge-b { background-color: #DBEAFE; color: #1E40AF; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
    .badge-c { background-color: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 4px; font-weight: 600; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🛒 Market Basket & Sentiment Clearance Control Tower</div>
    <div class="hero-subtitle">Enterprise Executive Dashboard | Preserving Gross Margin (GMROI) via Apriori Bundling & 3-Step NLP Review Diagnostics</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# DATA LOADING & ANALYTICS PIPELINE
# -------------------------------------------------------------
@st.cache_data
def load_enterprise_data():
    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    raw_dir = os.path.join(project_dir, "data", "raw")
    
    etl = ETLPipeline(raw_dir)
    try:
        r_df, rev_df = etl.load_raw_data()
        clean_retail = etl.clean_retail_data(r_df)
        sku_df = etl.aggregate_sku_level_metrics(clean_retail)
        clean_reviews = etl.clean_reviews_data(rev_df)
    except Exception as e:
        st.error(f"Data Connection Error: {e}")
        return None, None, None, None, None
        
    # Financial Analytics (ABC Pareto & GMROI Ratio)
    ifa = InventoryFinanceAnalytics()
    sku_abc = ifa.calculate_abc_classification(sku_df)
    sku_fin = ifa.calculate_gmroi(sku_abc)
    
    # 3-Step NLP Sentiment Diagnostics Workflow
    sd = SentimentDiagnostics()
    step1_reviews = sd.step1_vader_preprocessing(clean_reviews)
    step2_ngrams = sd.step2_tfidf_ngram_extraction(step1_reviews)
    step3_sku_sentiment = sd.step3_aggregate_business_insights(step1_reviews)
    
    # Market Basket Co-Purchasing Engine (Apriori)
    mba = MarketBasketAnalyzer(min_support=0.003, min_confidence=0.10, min_lift=1.1)
    b_matrix = mba.prepare_basket_matrix(clean_retail, max_items=100)
    freq_items = mba.run_apriori(b_matrix)
    rules = mba.generate_association_rules(freq_items)
    bundles = mba.find_bundle_recommendations(rules, sku_fin)
    
    return sku_fin, step1_reviews, step2_ngrams, step3_sku_sentiment, bundles

with st.spinner("Initializing Enterprise Data Pipeline & Running Analytics Engine..."):
    sku_df, reviews_df, ngrams_df, sku_sentiment_df, bundles_df = load_enterprise_data()

if sku_df is None or sku_df.empty:
    st.error("Data pipeline load failure. Please verify data sources.")
    st.stop()

# -------------------------------------------------------------
# SIDEBAR CONTROLS & CONTROLS
# -------------------------------------------------------------
st.sidebar.markdown("### ⚙️ Executive Control Panel")
st.sidebar.markdown("Filter portfolio scope and run real-time clearance margin simulations.")

abc_filter = st.sidebar.multiselect(
    "Inventory Velocity Filter (ABC)",
    options=sku_df['abc_class'].unique(),
    default=sku_df['abc_class'].unique(),
    help="A: Fast-moving anchors (top 70% revenue), B: Medium movers, C: Slow-moving clearance targets."
)

bundle_discount_slider = st.sidebar.slider(
    "Simulation Bundle Discount Tier (%)",
    min_value=10,
    max_value=40,
    value=20,
    step=5,
    help="Target discount applied to combined Anchor + Slow Mover bundles."
) / 100.0

st.sidebar.markdown("---")
st.sidebar.markdown("**Target Roles**: Merchandising VP | Supply Chain Director | Business Analyst")
st.sidebar.markdown("**System Version**: Enterprise v1.0")

df_filtered = sku_df[sku_df['abc_class'].isin(abc_filter)]

# -------------------------------------------------------------
# EXECUTIVE KPI SUMMARY ROW
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

total_skus = len(df_filtered)
avg_gmroi = df_filtered["gmroi"].mean()
c_stock_capital = df_filtered[df_filtered['abc_class'].str.startswith('C')]['avg_inventory_capital'].sum()
dead_stock_count = len(df_filtered[df_filtered['inventory_status'].str.contains('Dead Stock')])
margin_saved_est = c_stock_capital * 0.18 # Estimated 18% margin recovery via smart bundling

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Active SKUs Analyzed</div>
        <div class="kpi-value">{total_skus:,}</div>
        <div class="kpi-subtext">Across Apparel & Footwear</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Average GMROI Productivity</div>
        <div class="kpi-value">{avg_gmroi:.2f}x</div>
        <div class="kpi-subtext">Target Benchmark: 2.50x</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Slow-Mover Stock Capital</div>
        <div class="kpi-value">${c_stock_capital:,.0f}</div>
        <div class="kpi-subtext">At Risk of Holding Cost</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">High-Risk Dead Stock SKUs</div>
        <div class="kpi-value kpi-alert">{dead_stock_count}</div>
        <div class="kpi-subtext kpi-alert">Action Required (GMROI &lt; 1.20)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# NAVIGATION TABS
# -------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Portfolio Health & GMROI Matrix",
    "💬 Customer Sentiment & Diagnostic Insights",
    "🏷️ Smart Clearance & Bundle Simulator",
    "📋 Strategic Recommendations & BI Guide"
])

# -------------------------------------------------------------
# TAB 1: PORTFOLIO HEALTH & GMROI MATRIX
# -------------------------------------------------------------
with tab1:
    st.markdown("### Inventory Capital Efficiency vs. Ageing Matrix")
    st.markdown("This matrix evaluates stock age against Gross Margin Return on Inventory (GMROI) to identify high-risk clearance targets.")
    
    fig_scatter = px.scatter(
        df_filtered,
        x="inventory_age_days",
        y="gmroi",
        color="abc_class",
        size="stock_on_hand",
        hover_data=["ProductID", "Description", "total_revenue", "inventory_status"],
        color_discrete_map={
            "A (High Velocity)": "#10B981",
            "B (Medium Velocity)": "#3B82F6",
            "C (Slow Moving)": "#EF4444"
        },
        labels={
            "inventory_age_days": "Days in Inventory (Age)",
            "gmroi": "GMROI Ratio ($ Gross Margin / $ Inventory Investment)",
            "abc_class": "Velocity Tier"
        },
        height=500
    )
    fig_scatter.add_hline(
        y=1.20,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text="GMROI Alert Benchmark (1.20x)",
        annotation_position="bottom right"
    )
    fig_scatter.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(family="Inter, sans-serif", color="#0F172A"),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### High-Risk Inventory Clearance Action List")
    st.markdown("Products flagged as **C-Class (Slow Moving)** with **GMROI < 1.20x**, requiring immediate bundling clearance action.")
    
    dead_stock_df = df_filtered[df_filtered['abc_class'].str.startswith('C')].sort_values(by='gmroi', ascending=True)
    
    st.dataframe(
        dead_stock_df[[
            'ProductID', 'Description', 'abc_class', 'total_units_sold',
            'total_revenue', 'stock_on_hand', 'inventory_age_days', 'gmroi', 'inventory_status'
        ]].rename(columns={
            'ProductID': 'SKU ID',
            'Description': 'Product Name',
            'abc_class': 'ABC Tier',
            'total_units_sold': 'Units Sold',
            'total_revenue': 'Total Revenue ($)',
            'stock_on_hand': 'Stock On Hand',
            'inventory_age_days': 'Age (Days)',
            'gmroi': 'GMROI Index',
            'inventory_status': 'Inventory Risk Status'
        }),
        use_container_width=True,
        hide_index=True
    )

# -------------------------------------------------------------
# TAB 2: CUSTOMER SENTIMENT & DIAGNOSTIC INSIGHTS
# -------------------------------------------------------------
with tab2:
    st.markdown("### 💬 3-Step NLP Customer Sentiment Diagnostics")
    st.markdown("Uncovering why products are slow-moving by extracting customer feedback signals and categorizing operational root causes.")
    
    col_step1, col_step2 = st.columns(2)
    
    with col_step1:
        st.markdown("#### Step 1: Overall Customer Sentiment Distribution (VADER Polarity)")
        if reviews_df is not None and not reviews_df.empty:
            sentiment_counts = reviews_df['sentiment_label'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            
            fig_pie = px.pie(
                sentiment_counts,
                names='Sentiment',
                values='Count',
                color='Sentiment',
                color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#F59E0B'},
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No customer reviews dataset available.")
            
    with col_step2:
        st.markdown("#### Step 2: Voice-of-Customer Key Phrases (TF-IDF N-Grams)")
        st.markdown("Recurring 2-word and 3-word phrases extracted from negative customer reviews explaining *why* sales stagnate.")
        if ngrams_df is not None and not ngrams_df.empty:
            fig_ngrams = px.bar(
                ngrams_df.head(8),
                x='tfidf_score',
                y='ngram_phrase',
                orientation='h',
                color='tfidf_score',
                color_continuous_scale='Reds',
                labels={'tfidf_score': 'TF-IDF Impact Score', 'ngram_phrase': 'Customer Key Phrase'}
            )
            fig_ngrams.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_ngrams, use_container_width=True)
        else:
            st.info("No negative N-grams extracted.")

    st.markdown("---")
    
    st.markdown("#### Step 3: Root Cause Action Matrix")
    st.markdown("Categorizing complaints into actionable operational decisions for merchandising teams:")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("""
        **1. Sizing & Fit Flaws** (*"runs small", "tight sleeves"*)
        * **Action**: ❌ **STOP Price Discounts**
        * **Rationale**: Slashes won't fix high return rates; initiate fit pattern correction.
        """)
    with m2:
        st.markdown("""
        **2. Price Resistance** (*"overpriced for quality"*)
        * **Action**: ✅ **APPROVE Smart Bundle**
        * **Rationale**: Customer values item at lower price point; pair with high-margin Anchor.
        """)
    with m3:
        st.markdown("""
        **3. Quality & Material Defects** (*"cheap fabric", "ripped"*)
        * **Action**: ⚠️ **VENDOR RETURN (RTV)**
        * **Rationale**: Do not bundle defective stock; claim vendor credit.
        """)

    st.markdown("#### Customer Feedback Review Explorer")
    sentiment_filter_val = st.selectbox("Filter Feedback by Sentiment", ["All", "Negative", "Positive", "Neutral"])
    if sentiment_filter_val != "All":
        sub_rev = reviews_df[reviews_df['sentiment_label'] == sentiment_filter_val]
    else:
        sub_rev = reviews_df
        
    disp_cols = [c for c in ['rating', 'vader_compound', 'sentiment_label', 'root_cause_category', 'clean_review'] if c in sub_rev.columns]
    st.dataframe(sub_rev[disp_cols].head(15), use_container_width=True, hide_index=True)

# -------------------------------------------------------------
# TAB 3: SMART CLEARANCE & BUNDLE SIMULATOR
# -------------------------------------------------------------
with tab3:
    st.markdown("### 🏷️ Market Basket Co-Purchasing Rules (Apriori Mining)")
    st.markdown("Identified product association rules pairing high-demand **Anchor SKUs (A-Class)** with stagnant **Slow-Movers (C-Class)**.")
    
    if bundles_df is not None and not bundles_df.empty:
        st.dataframe(
            bundles_df[[
                'anchor_sku', 'anchor_desc', 'anchor_class',
                'slow_mover_sku', 'slow_mover_desc', 'slow_mover_class',
                'support', 'confidence', 'lift'
            ]].rename(columns={
                'anchor_sku': 'Anchor SKU',
                'anchor_desc': 'Anchor Product Name',
                'anchor_class': 'Anchor Tier',
                'slow_mover_sku': 'Slow-Mover SKU',
                'slow_mover_desc': 'Slow-Mover Product Name',
                'slow_mover_class': 'Slow-Mover Tier',
                'support': 'Support',
                'confidence': 'Confidence',
                'lift': 'Lift Metric'
            }).head(10),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        st.markdown("### ⚡ Live Bundle Margin Recovery Simulator")
        st.markdown("Interactively test the financial impact of creating a smart bundle vs. a standalone 50% clearance slash.")
        
        sim_c1, sim_c2 = st.columns(2)
        with sim_c1:
            anc_options = sku_df[sku_df['abc_class'].str.startswith('A')]['ProductID'].unique()
            anc_select = st.selectbox("Select Anchor Product (High Demand)", options=anc_options if len(anc_options)>0 else sku_df['ProductID'].unique(), index=0)
            anc_row = sku_df[sku_df['ProductID'] == anc_select].iloc[0]
            st.info(f"**Anchor SKU**: {anc_row['Description']}\n- Retail Price: **${anc_row['avg_unit_price']:.2f}**\n- Unit Cost: **${anc_row['avg_unit_cost']:.2f}**\n- Velocity Tier: **{anc_row['abc_class']}**")
            
        with sim_c2:
            slow_options = sku_df[sku_df['abc_class'].str.startswith('C')]['ProductID'].unique()
            slow_select = st.selectbox("Select Slow-Moving Target (C-Class)", options=slow_options if len(slow_options)>0 else sku_df['ProductID'].unique(), index=0)
            slow_row = sku_df[sku_df['ProductID'] == slow_select].iloc[0]
            st.warning(f"**Slow Mover SKU**: {slow_row['Description']}\n- Retail Price: **${slow_row['avg_unit_price']:.2f}**\n- Unit Cost: **${slow_row['avg_unit_cost']:.2f}**\n- Stock On Hand: **{slow_row['stock_on_hand']} units**")
            
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
        
        st.markdown("#### Simulation Financial Outcome")
        res_col1, res_col2, res_col3, res_col4 = st.columns(4)
        
        with res_col1:
            st.metric("Combined List Price", f"${sim_res['combined_original_price']:.2f}")
        with res_col2:
            st.metric(f"Smart Bundle Price ({int(bundle_discount_slider*100)}% off)", f"${sim_res['bundle_price']:.2f}")
        with res_col3:
            st.metric("Net Bundle Gross Margin", f"${sim_res['bundle_gross_margin']:.2f}", delta=f"{sim_res['bundle_margin_pct']}% Margin Rate")
        with res_col4:
            st.metric("Margin Dollars Saved vs Standalone Slash", f"${sim_res['margin_saved_vs_clearance']:.2f}", delta=f"+${sim_res['margin_saved_vs_clearance']:.2f} Saved")
            
    else:
        st.info("No co-purchasing association rules generated for current filters.")

# -------------------------------------------------------------
# TAB 4: STRATEGIC RECOMMENDATIONS & BI GUIDE
# -------------------------------------------------------------
with tab4:
    st.markdown("### 📋 Executive Action Plan & Roadmap")
    st.markdown("""
    #### 4-Phase Operational Execution Strategy
    1. **Phase 1: Automated ERP Alerts (Day 45)**: Trigger warning alerts in inventory systems when an SKU reaches 45+ Days in Inventory with GMROI < 1.20x.
    2. **Phase 2: Sentiment Filtering**: Run 3-Step NLP diagnostics on text reviews. Halt discounting for *Sizing Flaws* and forward patterns to product development. Approve bundle discounts for *Price Resistance*.
    3. **Phase 3: E-Commerce Bundle Placement**: Automatically inject high-lift Apriori bundle pairs directly into product detail pages (PDP) as *"Frequently Bought Together"*.
    4. **Phase 4: Dynamic Discount Pricing**: Apply 15%–20% bundle discounts to accelerate turnover while preserving total gross margin dollars above product cost.
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Enterprise BI Integration (Power BI & Tableau Specs)")
    st.markdown("Ready-to-copy calculated fields for integration into corporate business intelligence dashboards:")
    
    st.code("""
-- Power BI DAX: Gross Margin Return on Inventory (GMROI)
GMROI_Index = 
DIVIDE(
    SUM(Sales[LineRevenue]) - SUM(Sales[LineCOGS]),
    SUM(Inventory[StockOnHand]) * AVERAGE(Products[UnitCost]),
    0
)

-- Power BI DAX: ABC Velocity Classification
ABC_Class = 
VAR CumPercent = [Cumulative_Revenue_Percentage]
RETURN
IF(CumPercent <= 0.70, "A (High Velocity)",
    IF(CumPercent <= 0.90, "B (Medium Velocity)", "C (Slow Moving)"))
    """, language="sql")

st.sidebar.markdown("---")
st.sidebar.caption("🛒 **Market Basket & Sentiment Clearance Control Tower**")
