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
        
        # Margin Dollars Saved / Recovered
        # Anchor alone margin = anchor_price - anchor_cost
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
            results.append(res)
            
        eval_df = pd.DataFrame(results)
        return eval_df

if __name__ == "__main__":
    dbe = DynamicBundlingEngine()
    out = dbe.optimize_bundle_pricing(
        anchor_sku="SKU-101", anchor_price=80.0, anchor_cost=35.0,
        slow_sku="SKU-909", slow_price=40.0, slow_cost=20.0,
        bundle_discount_pct=0.20
    )
    print("Bundle Optimization Outcome:", out)
