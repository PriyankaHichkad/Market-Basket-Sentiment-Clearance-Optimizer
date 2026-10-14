import pandas as pd
import numpy as np

class DynamicBundlingEngine:
    """
    Dynamic Markdown & Margin Optimization Engine.
    Simulates margin recovery and financial outcomes of pairing slow-moving products 
    with high-demand anchor products vs. standalone heavy price slashes.
    """
    def __init__(self, holding_cost_rate: float = 0.25):
        self.holding_cost_rate = holding_cost_rate

    def optimize_bundle_pricing(
        self,
        anchor_sku: str,
        anchor_price: float,
        anchor_cost: float,
        slow_sku: str,
        slow_price: float,
        slow_cost: float,
        bundle_discount_pct: float = 0.20,
        standalone_clearance_discount_pct: float = 0.50
    ) -> dict:
        """
        Calculates financial trade-offs between Standalone Clearance vs. Smart Bundle Strategy.
        """
        # Standalone Clearance Strategy (e.g. 50% off slow-mover alone)
        standalone_markdown_price = slow_price * (1 - standalone_clearance_discount_pct)
        standalone_margin = standalone_markdown_price - slow_cost
        
        # Combined Bundle Strategy
        combined_original_price = anchor_price + slow_price
        bundle_price = combined_original_price * (1 - bundle_discount_pct)
        total_bundle_cost = anchor_cost + slow_cost
        bundle_gross_margin = bundle_price - total_bundle_cost
        
        # Margin Dollars Saved / Recovered:
        # margin_delta = slow_price * (standalone_clearance_discount_pct - bundle_discount_pct) - anchor_price * bundle_discount_pct
        # Mathematically accretive (margin_delta >= 0) iff:
        # anchor_price / slow_price <= (standalone_clearance_discount_pct - bundle_discount_pct) / bundle_discount_pct
        # E.g., at 50% clearance vs 20% bundle discount, accretive only when anchor_price <= 1.5 * slow_price.
        anchor_alone_margin = anchor_price - anchor_cost
        combined_unbundled_margin = anchor_alone_margin + standalone_margin
        margin_delta = bundle_gross_margin - combined_unbundled_margin
        
        bundle_margin_pct = (bundle_gross_margin / bundle_price) if bundle_price > 0 else 0.0
        
        return {
            'anchor_sku': anchor_sku,
            'slow_sku': slow_sku,
            'anchor_price': anchor_price,
            'slow_price': slow_price,
            'combined_original_price': combined_original_price,
            'bundle_discount_pct': bundle_discount_pct,
            'bundle_price': round(bundle_price, 2),
            'bundle_gross_margin': round(bundle_gross_margin, 2),
            'bundle_margin_pct': round(bundle_margin_pct * 100, 1),
            'standalone_clearance_margin': round(standalone_margin, 2),
            'margin_saved_vs_clearance': round(margin_delta, 2),
            'strategy_recommendation': 'Approve Bundle' if margin_delta >= 0 else 'Review Pricing'
        }

    def evaluate_portfolio_clearance(
        self,
        bundles_df: pd.DataFrame,
        sku_analytics_df: pd.DataFrame,
        discount_tier: float = 0.20
    ) -> pd.DataFrame:
        """
        Runs portfolio-wide clearance scenario evaluation across identified candidate bundles.
        """
        if bundles_df.empty or sku_analytics_df.empty:
            return pd.DataFrame()
            
        cost_map = dict(zip(sku_analytics_df['ProductID'].astype(str), sku_analytics_df['avg_unit_cost']))
        price_map = dict(zip(sku_analytics_df['ProductID'].astype(str), sku_analytics_df['avg_unit_price']))
        
        results = []
        for _, row in bundles_df.iterrows():
            anc_sku = str(row['anchor_sku'])
            slw_sku = str(row['slow_mover_sku'])
            
            anc_price = price_map.get(anc_sku, row.get('anchor_price', 50.0))
            anc_cost = cost_map.get(anc_sku, anc_price * 0.50)
            
            slw_price = price_map.get(slw_sku, row.get('slow_mover_price', 40.0))
            slw_cost = cost_map.get(slw_sku, slw_price * 0.50)
            
            res = self.optimize_bundle_pricing(
                anchor_sku=anc_sku,
                anchor_price=anc_price,
                anchor_cost=anc_cost,
                slow_sku=slw_sku,
                slow_price=slw_price,
                slow_cost=slw_cost,
                bundle_discount_pct=discount_tier
            )
            res['anchor_desc'] = row.get('anchor_desc', anc_sku)
            res['slow_mover_desc'] = row.get('slow_mover_desc', slw_sku)
            res['lift'] = row.get('lift', 1.0)
            res['price_ratio'] = round(anc_price / slw_price, 2) if slw_price > 0 else 0.0
            results.append(res)
            
        eval_df = pd.DataFrame(results)
        return eval_df

    # -------------------------------------------------------------
    # SELL-THROUGH SCENARIO MODEL
    # -------------------------------------------------------------
    # The per-unit comparison in optimize_bundle_pricing assumes the same number
    # of units clear under every strategy. In practice the reason to bundle is
    # that it should clear MORE stock than a markdown. These methods make that
    # assumption an explicit, adjustable input instead of leaving it implicit.
    #
    # Nothing here is measured from the data: sell-through and anchor
    # incrementality are scenario assumptions. Results should be reported as
    # "under assumptions X, bundling wins/loses", never as observed outcomes.

    def simulate_clearance_scenario(
        self,
        anchor_price: float,
        anchor_cost: float,
        slow_price: float,
        slow_cost: float,
        slow_stock_units: float,
        markdown_discount_pct: float = 0.50,
        bundle_discount_pct: float = 0.20,
        bundle_discount_scope: str = "both",
        markdown_sell_through: float = 0.60,
        bundle_sell_through: float = 0.80,
        anchor_incremental_share: float = 0.30,
        window_days: int = 45,
    ) -> dict:
        """
        Compares gross profit over a clearance window for one slow mover under
        two strategies, relative to doing nothing:

        - Standalone markdown: markdown_sell_through of the slow-mover stock
          clears at (1 - markdown_discount_pct) of list price.
        - Bundle: bundle_sell_through of the stock clears inside bundles with
          the anchor. Only anchor_incremental_share of those anchor units are
          new sales; the rest would have sold at full price anyway, so the
          bundle discount on them is given away (cannibalization).

        Unsold slow-mover units carry holding cost for the window under both.

        bundle_discount_scope:
            'both'      discount applies to anchor + slow mover (blanket bundle)
            'slow_only' anchor stays at list price, discount applies to the
                        slow mover only
        """
        if bundle_discount_scope not in ("both", "slow_only"):
            raise ValueError("bundle_discount_scope must be 'both' or 'slow_only'")
        for name, val in (
            ("markdown_sell_through", markdown_sell_through),
            ("bundle_sell_through", bundle_sell_through),
            ("anchor_incremental_share", anchor_incremental_share),
        ):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")

        stock = max(0.0, float(slow_stock_units))
        holding_per_unit = slow_cost * self.holding_cost_rate * window_days / 365.0

        # Strategy A: standalone markdown on the slow mover
        md_units = stock * markdown_sell_through
        md_unit_margin = slow_price * (1 - markdown_discount_pct) - slow_cost
        md_profit = md_units * md_unit_margin - (stock - md_units) * holding_per_unit

        # Strategy B: bundle with the anchor
        if bundle_discount_scope == "both":
            bundle_price = (anchor_price + slow_price) * (1 - bundle_discount_pct)
        else:
            bundle_price = anchor_price + slow_price * (1 - bundle_discount_pct)
        bundle_margin = bundle_price - anchor_cost - slow_cost
        cannibalized_margin = (1 - anchor_incremental_share) * (anchor_price - anchor_cost)
        gain_per_bundle = bundle_margin - cannibalized_margin

        b_units = stock * bundle_sell_through
        b_profit = b_units * gain_per_bundle - (stock - b_units) * holding_per_unit

        # Bundle sell-through at which both strategies earn the same profit.
        # Profit is linear in sell-through, so this has a closed form.
        denom = gain_per_bundle + holding_per_unit
        if stock > 0 and denom > 0:
            breakeven = (md_profit / stock + holding_per_unit) / denom
        else:
            breakeven = float("nan")

        return {
            "markdown_profit": round(md_profit, 2),
            "bundle_profit": round(b_profit, 2),
            "profit_delta": round(b_profit - md_profit, 2),
            "gain_per_bundle": round(gain_per_bundle, 2),
            "breakeven_bundle_sell_through": None if np.isnan(breakeven) else round(breakeven, 3),
            "bundle_wins": bool(b_profit > md_profit),
        }

    def evaluate_clearance_scenarios(
        self,
        bundles_df: pd.DataFrame,
        sku_analytics_df: pd.DataFrame,
        **scenario_params,
    ) -> pd.DataFrame:
        """
        Runs simulate_clearance_scenario for every candidate bundle, using the
        slow mover's modeled stock_on_hand as the units to clear.
        """
        if bundles_df.empty or sku_analytics_df.empty:
            return pd.DataFrame()

        lookup = sku_analytics_df.assign(_pid=sku_analytics_df["ProductID"].astype(str)).set_index("_pid")
        rows = []
        for _, b in bundles_df.iterrows():
            anc, slw = str(b["anchor_sku"]), str(b["slow_mover_sku"])
            if anc not in lookup.index or slw not in lookup.index:
                continue
            a, s = lookup.loc[anc], lookup.loc[slw]
            res = self.simulate_clearance_scenario(
                anchor_price=float(a["avg_unit_price"]),
                anchor_cost=float(a["avg_unit_cost"]),
                slow_price=float(s["avg_unit_price"]),
                slow_cost=float(s["avg_unit_cost"]),
                slow_stock_units=float(s["stock_on_hand"]),
                **scenario_params,
            )
            res.update({
                "anchor_sku": anc,
                "slow_mover_sku": slw,
                "anchor_price": float(a["avg_unit_price"]),
                "slow_price": float(s["avg_unit_price"]),
                "slow_stock_units": float(s["stock_on_hand"]),
                "lift": b.get("lift", np.nan),
            })
            rows.append(res)
        return pd.DataFrame(rows)

    @staticmethod
    def summarize_scenario(scenario_df: pd.DataFrame) -> dict:
        """Portfolio-level summary of evaluate_clearance_scenarios output."""
        if scenario_df.empty:
            return {}
        be = pd.to_numeric(scenario_df["breakeven_bundle_sell_through"], errors="coerce")
        # Breakeven below 0: the bundle beats the markdown even at zero sell-through
        # (the markdown itself loses money). Above 1, or undefined: no sell-through
        # can make the bundle win. Only 0..1 means the sell-through assumption decides.
        always = be < 0
        conditional = (be >= 0) & (be <= 1.0)
        never = (be > 1.0) | be.isna()
        return {
            "bundles": int(len(scenario_df)),
            "bundles_beating_markdown": int(scenario_df["bundle_wins"].sum()),
            "win_rate": float(scenario_df["bundle_wins"].mean()),
            "median_profit_delta": float(scenario_df["profit_delta"].median()),
            "total_profit_delta": float(scenario_df["profit_delta"].sum()),
            "wins_at_any_sell_through": int(always.sum()),
            "depends_on_sell_through": int(conditional.sum()),
            "cannot_win": int(never.sum()),
            "median_breakeven_sell_through": float(be[conditional].median()) if conditional.any() else float("nan"),
        }

if __name__ == "__main__":
    dbe = DynamicBundlingEngine()
    out = dbe.optimize_bundle_pricing(
        anchor_sku="SKU-101", anchor_price=80.0, anchor_cost=35.0,
        slow_sku="SKU-909", slow_price=40.0, slow_cost=20.0,
        bundle_discount_pct=0.20
    )
    print("Bundle Optimization Outcome:", out)
