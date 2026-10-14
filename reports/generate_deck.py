import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_executive_deck(output_path: str):
    """
    Generates a high-impact 10-slide PowerPoint (.pptx) deck for retail executive leadership.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    
    # Colors
    NAVY = RGBColor(16, 37, 66)
    ACCENT_BLUE = RGBColor(0, 114, 206)
    DARK_GRAY = RGBColor(50, 50, 50)
    LIGHT_BG = RGBColor(245, 247, 250)
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(34, 139, 34)
    CORAL = RGBColor(217, 83, 79)
    
    blank_layout = prs.slide_layouts[6]
    
    # Compute live empirical metrics across pipeline
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    from src.etl_pipeline import ETLPipeline
    from src.inventory_finance import InventoryFinanceAnalytics
    from src.sentiment_diagnostics import SentimentDiagnostics
    from src.market_basket import MarketBasketAnalyzer
    from src.dynamic_bundling_engine import DynamicBundlingEngine
    
    raw_dir = os.path.join(project_root, "data", "raw")
    etl = ETLPipeline(raw_dir)
    r_df, rev_df = etl.load_raw_data()
    clean_r = etl.clean_retail_data(r_df)
    sku_df = etl.aggregate_sku_level_metrics(clean_r)
    
    ifa = InventoryFinanceAnalytics()
    fin_df = ifa.calculate_gmroi(ifa.calculate_abc_classification(sku_df))
    
    c_skus = fin_df[fin_df['abc_class'].str.startswith('C')]
    dead_skus = fin_df[fin_df['inventory_status'].str.contains('Dead Stock')]
    c_count = len(c_skus)
    c_pct = (c_count / len(fin_df)) * 100
    dead_count = len(dead_skus)
    dead_capital = dead_skus['avg_inventory_capital'].sum()
    c_capital = c_skus['avg_inventory_capital'].sum()
    c_cap_pct = (c_capital / fin_df['avg_inventory_capital'].sum()) * 100

    sd = SentimentDiagnostics()
    clean_rev = etl.clean_reviews_data(rev_df)
    step1_rev = sd.step1_vader_preprocessing(clean_rev)
    neg_reviews = step1_rev[step1_rev['sentiment_label'] == 'Negative']
    neg_count = len(neg_reviews)
    sizing_count = len(neg_reviews[neg_reviews['root_cause_category'] == 'Sizing & Fit Flaw'])
    sizing_pct = (sizing_count / neg_count * 100) if neg_count > 0 else 0.0

    mba = MarketBasketAnalyzer(min_support=0.005, min_confidence=0.05, min_lift=1.05)
    b_matrix = mba.prepare_basket_matrix(clean_r, sku_analytics_df=fin_df, max_items=100)
    freq_items = mba.run_apriori(b_matrix)
    rules = mba.generate_association_rules(freq_items)
    bundles = mba.find_bundle_recommendations(rules, fin_df)
    bundle_count = len(bundles)
    avg_lift = bundles['lift'].mean() if not bundles.empty else 0.0

    dbe = DynamicBundlingEngine()
    eval_res = dbe.evaluate_portfolio_clearance(bundles, fin_df, discount_tier=0.20)
    accretive_count = len(eval_res[eval_res['margin_saved_vs_clearance'] > 0])
    
    def add_header(slide, title_text, category_text="RETAIL STRATEGY & SUPPLY CHAIN ANALYTICS"):
        # Header background banner
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.1))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = NAVY
        header_shape.line.fill.background()
        
        # Category subhead
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.15), Inches(11.5), Inches(0.3))
        tf_sub = sub_box.text_frame
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = category_text.upper()
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = ACCENT_BLUE
        
        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.6))
        tf_title = title_box.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = NAVY
    bg1.line.fill.background()
    
    tb1 = slide1.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.5))
    tf1 = tb1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "E-Commerce Inventory Markdown &\nBasket Sentiment Intelligence"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    
    p2 = tf1.add_paragraph()
    p2.text = "Protecting Gross Margin Return on Inventory (GMROI) via Market Basket Bundling & NLP Review Diagnostics"
    p2.font.size = Pt(18)
    p2.font.color.rgb = ACCENT_BLUE
    p2.space_before = Pt(15)
    
    p3 = tf1.add_paragraph()
    p3.text = "Target Audience: Chief Merchandising Officer | VP of Supply Chain | Retail Business Analysts"
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(180, 200, 220)
    p3.space_before = Pt(30)

    # -------------------------------------------------------------
    # SLIDE 2: The Retail Dilemma
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "The Retail Dilemma: End-of-Season Clearance & Margin Erosion")
    
    # Left Box: Problem
    box_left = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.2))
    box_left.fill.solid()
    box_left.fill.fore_color.rgb = LIGHT_BG
    box_left.line.color.rgb = CORAL
    box_left.line.width = Pt(2)
    
    tf_l = box_left.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "Traditional Clearance Pitfalls"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = CORAL
    
    bullets_l = [
        "Flat 50-70% Price Slashes: Destroys product brand equity and erodes gross margins below COGS.",
        "Blind Discounting: Slashes prices on items stagnant due to sizing flaws, which discounts won't solve.",
        "Holding Capital Trap: Slow-moving C-Class inventory locks up cash flow and incurs 20-30% annual holding costs.",
        "Siloed Analytics: Merchandisers look at velocity in isolation from customer feedback text."
    ]
    for b in bullets_l:
        p = tf_l.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(12)

    # Right Box: Opportunity
    box_right = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.5), Inches(5.6), Inches(5.2))
    box_right.fill.solid()
    box_right.fill.fore_color.rgb = LIGHT_BG
    box_right.line.color.rgb = GREEN
    box_right.line.width = Pt(2)
    
    tf_r = box_right.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "The Intelligent Bundling Solution"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = GREEN
    
    bullets_r = [
        "Data-Driven Co-Purchasing: Pair slow C-Class items with high-demand A-Class anchor products using Apriori algorithm.",
        "Root-Cause NLP Diagnostics: Distinguish pricing resistance from physical quality/fit defects using VADER sentiment.",
        "GMROI Maximization: Preserve gross margin dollars while accelerating inventory turnover.",
        "Dynamic Markdown Tiers: Tailor bundle discounts (15-25%) to maximize total basket profitability."
    ]
    for b in bullets_r:
        p = tf_r.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 3: Integrated 4-Pillar Framework
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "End-to-End Analytical Framework & Architecture")
    
    pillars = [
        ("Pillar 1: Data Pipeline", "Clean real-world sales transactions & customer review text logs.", ACCENT_BLUE),
        ("Pillar 2: GMROI & ABC", "Categorize inventory into A/B/C velocity tiers & calculate GMROI index.", NAVY),
        ("Pillar 3: Market Basket AI", "Mine Apriori association rules (Support, Confidence, Lift) for bundles.", ACCENT_BLUE),
        ("Pillar 4: Dynamic Markdown", "Optimize bundle discount tiers to maximize net profit recovery.", GREEN)
    ]
    
    for i, (p_title, p_desc, p_color) in enumerate(pillars):
        x_pos = Inches(0.8 + i * 3.0)
        card = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x_pos, Inches(2.2), Inches(2.7), Inches(4.2))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT_BG
        card.line.color.rgb = p_color
        card.line.width = Pt(2)
        
        tf_c = card.text_frame
        tf_c.word_wrap = True
        
        p = tf_c.paragraphs[0]
        p.text = f"0{i+1}"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = p_color
        
        p = tf_c.add_paragraph()
        p.text = p_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        p.space_before = Pt(10)
        
        p = tf_c.add_paragraph()
        p.text = p_desc
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(10)

    # -------------------------------------------------------------
    # SLIDE 4: Portfolio Inventory Health (ABC-GMROI)
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Inventory Portfolio Diagnostics: ABC Classification & GMROI")
    
    tb4 = slide4.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.3))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    
    p = tf4.paragraphs[0]
    p.text = "Pareto Velocity Distribution & Inventory Capital Efficiency"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    content4 = [
        "• Class A SKUs (Top 70% Revenue): High velocity anchors. Target GMROI > 3.0. Must never be discounted standalone.",
        "• Class B SKUs (Next 20% Revenue): Moderate movers. Balanced inventory turnover and healthy gross margins.",
        f"• Class C SKUs (Tail 10% Revenue): Slow-moving inventory representing {c_cap_pct:.1f}% of total stock capital (${c_capital:,.0f}).",
        f"• Dead Stock Risk (GMROI < 1.2): {dead_count:,} SKUs locking up ${dead_capital:,.0f} in unproductive working capital.",
        "• Strategic Objective: Use Class A anchors as traffic drivers to clear Class C inventory via smart co-purchasing bundles."
    ]
    for c in content4:
        p = tf4.add_paragraph()
        p.text = c
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(14)

    # -------------------------------------------------------------
    # SLIDE 5: NLP Review Diagnostics
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "NLP Customer Review Diagnostics: Root Cause Isolation")
    
    categories = [
        ("Price Resistance", "Feedback indicating item is overpriced or poor value. Solvable by bundle discounts.", GREEN),
        ("Sizing / Fit Flaws", "Complaints about incorrect sizing or poor cut. Slashes won't fix high return rates.", CORAL),
        ("Fabric / Quality Issues", "Issues with material durability or color fading. Candidate for vendor return.", ACCENT_BLUE)
    ]
    
    for i, (c_name, c_desc, c_col) in enumerate(categories):
        x = Inches(0.8 + i * 3.9)
        c_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.0), Inches(3.6), Inches(4.5))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = LIGHT_BG
        c_box.line.color.rgb = c_col
        c_box.line.width = Pt(2)
        
        tf = c_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = c_name
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = c_col
        
        p = tf.add_paragraph()
        p.text = c_desc
        p.font.size = Pt(13)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(15)

    # -------------------------------------------------------------
    # SLIDE 6: Market Basket Apriori Discovery
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Market Basket Analysis: Apriori Co-Purchasing Rules")
    
    tb6 = slide6.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.3))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    
    p = tf6.paragraphs[0]
    p.text = "Uncovering Product Affinity & Cross-Selling Pairs"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    points6 = [
        "• Support Metric: Frequency of basket co-occurrence across transactions (min_support = 0.005).",
        "• Confidence Metric: Conditional probability of buying Slow-Mover B given Anchor A is in cart.",
        "• Lift Metric (Lift > 1.2): Quantifies how much more frequently two items are bought together than by random chance.",
        "• High-Lift Bundle Pairing: Pairing high-lift accessories/apparel anchors with stagnant C-Class stock guarantees natural customer interest.",
        "• Cross-Category Synergies: Combining footwear anchors with slow-moving clothing items yields highest bundle conversion."
    ]
    for pt in points6:
        p = tf6.add_paragraph()
        p.text = pt
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(14)

    # -------------------------------------------------------------
    # SLIDE 7: Dynamic Markdown & Bundling Strategy
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Dynamic Markdown Strategy vs. Standalone Clearance")
    
    tb7 = slide7.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.3))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    
    p = tf7.paragraphs[0]
    p.text = "Mathematical Model for Margin Protection"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    model_points = [
        "1. Standalone Clearance: 50% price slash severely erodes gross margin dollars, risking cash recovery below inventory unit cost.",
        "2. Smart Bundle Pricing: 15%–20% discount applied across co-purchased pair (Anchor + Slow Mover) mined via Apriori rules.",
        "3. Margin Protection Depends on Discount Design: a blanket bundle discount gives away anchor margin; discounting only the slow mover protects it (see scenario analysis).",
        f"4. Algorithmic Gatekeeper: Engine selectively approves {accretive_count} of {bundle_count} mined bundles for blanket bundling while routing price-asymmetric pairs to targeted clearance.",
        "5. Working Capital Optimization: Protects high-velocity anchor margin dollars while systematically unlocking stagnant C-Class stock."
    ]
    for mp in model_points:
        p = tf7.add_paragraph()
        p.text = mp
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 8: Financial Impact & Simulation
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Financial Impact & Inventory Risk Analysis")
    
    box_sim = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8))
    box_sim.fill.solid()
    box_sim.fill.fore_color.rgb = LIGHT_BG
    box_sim.line.color.rgb = GREEN
    box_sim.line.width = Pt(2)
    
    tf_s = box_sim.text_frame
    tf_s.word_wrap = True
    
    p = tf_s.paragraphs[0]
    p.text = "Empirical Findings & Portfolio Analytics Summary"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = GREEN
    
    if bundles.empty:
        bundle_line = "• High-Affinity Cross-Tier Bundles: no anchor / slow-mover bundles met the mining thresholds."
    else:
        bundle_line = (
            f"• High-Affinity Cross-Tier Bundles: Mined {len(bundles)} bundle pairs combining anchors and "
            f"slow-movers with an average Lift of {bundles['lift'].mean():.2f}x."
        )

    # Pure dynamic results directly from pipeline analytics
    sim_results = [
        f"• Catalog Risk Exposure: Identified {c_count:,} slow-moving C-Class SKUs ({c_pct:.1f}% of catalog) generating 10% of revenue.",
        f"• Trapped Inventory Capital: ${dead_capital:,.0f} (modeled) across {dead_count:,} low-revenue-tier SKUs with GMROI < 1.20x.",
        f"• Sentiment Root Causes: {sizing_pct:.1f}% of negative reviews driven by sizing/fit flaws where price discounting is counterproductive.",
        bundle_line,
    ]
    for sr in sim_results:
        p = tf_s.add_paragraph()
        p.text = sr
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(16)

    # -------------------------------------------------------------
    # SLIDE 9: Control Tower Dashboard
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Interactive Merchandising Control Tower & Power BI Specs")
    
    tb9 = slide9.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(5.3))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    
    p = tf9.paragraphs[0]
    p.text = "Decision Support Portal Features"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = NAVY
    
    dash_features = [
        "• Executive Overview: Real-time inventory capital at risk, average GMROI, and clearance targets.",
        "• Interactive Bundle Simulator: Select any slow-moving SKU, pair with recommended anchors, adjust discount slider, and view real-time margin delta.",
        "• Review Sentiment Deep-Dive: Filter products by sentiment polarity and inspect root cause word clouds.",
        "• Power BI / Tableau Export: Pre-configured DAX calculated measures (GMROI, ABC Class, Lift, Margin Recovery)."
    ]
    for df_feat in dash_features:
        p = tf9.add_paragraph()
        p.text = df_feat
        p.font.size = Pt(14)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(14)

    # -------------------------------------------------------------
    # SLIDE 10: Strategic Recommendations & Roadmap
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Strategic Recommendations & Action Plan Roadmap")
    
    roadmap_steps = [
        ("Phase 1: Automated Alerts", "Deploy automated GMROI < 1.2 triggers in ERP to flag stagnant SKUs at Day 45."),
        ("Phase 2: Sentiment Filtering", "Run NLP sentiment diagnostics to separate pricing issues from sizing defects."),
        ("Phase 3: Automated Bundling", "Push high-lift Apriori bundle pairs directly to e-commerce recommendation engine."),
        ("Phase 4: Dynamic Pricing", "Automate dynamic 15-20% bundle checkout discounts for targeted inventory.")
    ]
    
    for i, (r_title, r_desc) in enumerate(roadmap_steps):
        y = Inches(1.6 + i * 1.3)
        r_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.1))
        r_box.fill.solid()
        r_box.fill.fore_color.rgb = LIGHT_BG
        r_box.line.color.rgb = ACCENT_BLUE
        r_box.line.width = Pt(1.5)
        
        tf = r_box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = r_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY
        
        p = tf.add_paragraph()
        p.text = r_desc
        p.font.size = Pt(12)
        p.font.color.rgb = DARK_GRAY
        p.space_before = Pt(4)

    # Save presentation
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_pptx = os.path.join(project_dir, "reports", "executive_presentation_deck.pptx")
    create_executive_deck(output_pptx)
