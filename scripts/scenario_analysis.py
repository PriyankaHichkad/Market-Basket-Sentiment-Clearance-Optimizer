"""
Sell-through scenario analysis for the mined cross-tier bundles.

Nothing printed here is observed sales data. Sell-through, anchor
incrementality and costs are modeled assumptions; the output answers
"under these assumptions, does bundling beat a 50% markdown?" and
"how much extra sell-through would bundling need to break even?".

Run:  python3 scripts/scenario_analysis.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.etl_pipeline import ETLPipeline
from src.inventory_finance import InventoryFinanceAnalytics
from src.market_basket import MarketBasketAnalyzer
from src.dynamic_bundling_engine import DynamicBundlingEngine

# Baseline assumptions (all adjustable; see README "Scenario assumptions")
MARKDOWN_SELL_THROUGH = 0.60   # share of slow-mover stock a 50% markdown clears in the window
BUNDLE_SELL_THROUGH = 0.80     # share a bundle clears in the same window
ANCHOR_INCREMENTAL = 0.30      # share of bundled anchor units that are genuinely new sales
BUNDLE_DISCOUNT = 0.20
WINDOW_DAYS = 45


def load_bundles():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    etl = ETLPipeline(os.path.join(project_dir, "data", "raw"))
    retail, _ = etl.load_raw_data()
    clean = etl.clean_retail_data(retail)
    sku_df = etl.aggregate_sku_level_metrics(clean)

    ifa = InventoryFinanceAnalytics()
    fin_df = ifa.calculate_gmroi(ifa.calculate_abc_classification(sku_df))

    # Same mining parameters as scripts/audit_metrics.py
    mba = MarketBasketAnalyzer(min_support=0.005, min_confidence=0.05, min_lift=1.05)
    matrix = mba.prepare_basket_matrix(clean, sku_analytics_df=fin_df, max_items=100)
    rules = mba.generate_association_rules(mba.run_apriori(matrix))
    bundles = mba.find_bundle_recommendations(rules, fin_df)
    return bundles, fin_df


def run(bundles, fin_df, **overrides):
    params = dict(
        markdown_sell_through=MARKDOWN_SELL_THROUGH,
        bundle_sell_through=BUNDLE_SELL_THROUGH,
        anchor_incremental_share=ANCHOR_INCREMENTAL,
        bundle_discount_pct=BUNDLE_DISCOUNT,
        window_days=WINDOW_DAYS,
        bundle_discount_scope="both",
    )
    params.update(overrides)
    dbe = DynamicBundlingEngine()
    df = dbe.evaluate_clearance_scenarios(bundles, fin_df, **params)
    return df, dbe.summarize_scenario(df)


def main():
    bundles, fin_df = load_bundles()
    print("=" * 72)
    print("SELL-THROUGH SCENARIO ANALYSIS  (modeled assumptions, not observed data)")
    print("=" * 72)
    print(f"Mined cross-tier bundles evaluated: {len(bundles)}")
    print(
        f"Baseline assumptions: markdown clears {MARKDOWN_SELL_THROUGH:.0%}, "
        f"bundle clears {BUNDLE_SELL_THROUGH:.0%}, anchor incremental {ANCHOR_INCREMENTAL:.0%}, "
        f"bundle discount {BUNDLE_DISCOUNT:.0%}, window {WINDOW_DAYS}d, markdown 50% off"
    )

    print("\n[Baseline scenario, by discount design]")
    for scope in ("both", "slow_only"):
        _, s = run(bundles, fin_df, bundle_discount_scope=scope)
        be = s["median_breakeven_sell_through"]
        be_txt = f"{be:.0%}" if be == be else "n/a"
        print(
            f"  scope={scope:<9} bundles beating markdown: {s['bundles_beating_markdown']}/{s['bundles']} "
            f"| median delta ${s['median_profit_delta']:,.2f} | total delta ${s['total_profit_delta']:,.2f}"
        )
        print(
            f"  {'':<15} win at any sell-through: {s['wins_at_any_sell_through']} | "
            f"depend on sell-through: {s['depends_on_sell_through']} (median breakeven {be_txt}) | "
            f"cannot win: {s['cannot_win']}"
        )

    for scope in ("both", "slow_only"):
        print(f"\n[Sensitivity: bundles beating markdown, scope={scope}]")
        print("  rows = anchor incremental share, cols = bundle sell-through")
        sts = [0.60, 0.70, 0.80, 0.90]
        header = "  incr \\ sell-through " + "".join(f"{int(st*100):>8}%" for st in sts)
        print(header)
        for incr in (0.0, 0.3, 0.6, 1.0):
            cells = []
            for st in sts:
                _, s = run(bundles, fin_df, bundle_discount_scope=scope,
                           bundle_sell_through=st, anchor_incremental_share=incr)
                cells.append(f"{s['bundles_beating_markdown']:>3}/{s['bundles']:<3} ")
            print(f"  {incr:>19.0%} " + "".join(f"{c:>9}" for c in cells))

    print("\n[Where the baseline blanket bundle loses: anchor/slow price ratio]")
    df, _ = run(bundles, fin_df, bundle_discount_scope="both")
    df["price_ratio"] = df["anchor_price"] / df["slow_price"].clip(lower=0.01)
    df["ratio_band"] = pd.cut(df["price_ratio"], [0, 2, 5, 20, 1e9], labels=["<=2x", "2-5x", "5-20x", ">20x"])
    band = df.groupby("ratio_band", observed=True).agg(
        bundles=("bundle_wins", "size"), wins=("bundle_wins", "sum"),
        median_delta=("profit_delta", "median"))
    print(band.round(2).to_string())
    print("=" * 72)


if __name__ == "__main__":
    main()
