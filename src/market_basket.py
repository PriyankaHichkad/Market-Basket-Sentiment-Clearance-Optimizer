import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules

class MarketBasketAnalyzer:
    """
    Market Basket Analysis Engine using Apriori Algorithm.
    Mines co-purchasing patterns and association rules from transaction logs
    to identify anchor products to pair with slow-moving inventory.
    """
    def __init__(self, min_support: float = 0.005, min_confidence: float = 0.15, min_lift: float = 1.2):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift

    def prepare_basket_matrix(self, df_retail: pd.DataFrame, max_items: int = 300) -> pd.DataFrame:
        """
        Transforms transaction logs into a binary One-Hot Encoded basket matrix.
        Rows: InvoiceNo | Columns: Product Description / ID | Values: 1 (Bought) / 0 (Not bought)
        """
        print("Building Market Basket matrix...")
        # Use top N most frequent products to keep matrix memory efficient
        top_products = df_retail['ProductID'].value_counts().head(max_items).index
        df_filtered = df_retail[df_retail['ProductID'].isin(top_products)]
        
        basket = (df_filtered.groupby(['InvoiceNo', 'ProductID'])['Quantity']
                  .sum().unstack().reset_index().fillna(0)
                  .set_index('InvoiceNo'))
                  
        # Convert quantities to boolean (True if > 0 else False)
        basket_binary = (basket > 0)
        print(f"Basket Matrix Shape: {basket_binary.shape[0]:,} invoices x {basket_binary.shape[1]:,} SKUs")
        return basket_binary

    def run_apriori(self, basket_matrix: pd.DataFrame) -> pd.DataFrame:
        """Runs Apriori algorithm to find frequent itemsets."""
        print(f"Executing Apriori (min_support={self.min_support})...")
        frequent_itemsets = apriori(basket_matrix, min_support=self.min_support, use_colnames=True)
        print(f"Found {len(frequent_itemsets):,} frequent itemsets")
        return frequent_itemsets

    def generate_association_rules(self, frequent_itemsets: pd.DataFrame) -> pd.DataFrame:
        """Generates association rules from frequent itemsets."""
        if frequent_itemsets.empty:
            print("No frequent itemsets found. Lower min_support threshold.")
            return pd.DataFrame()

        print(f"Generating Association Rules (min_confidence={self.min_confidence}, min_lift={self.min_lift})...")
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        rules = rules[rules['lift'] >= self.min_lift].sort_values(by='lift', ascending=False).reset_index(drop=True)
        
        # Convert frozensets to clean string lists
        rules['antecedents_str'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        rules['consequents_str'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
        
        print(f"Generated {len(rules):,} high-lift association rules")
        return rules

    def find_bundle_recommendations(self, rules: pd.DataFrame, sku_analytics_df: pd.DataFrame) -> pd.DataFrame:
        """
        Pairs slow-moving C-Class products with high-demand A/B-Class products.
        """
        if rules.empty or sku_analytics_df.empty:
            return pd.DataFrame()
            
        abc_map = dict(zip(sku_analytics_df['ProductID'].astype(str), sku_analytics_df['abc_class']))
        price_map = dict(zip(sku_analytics_df['ProductID'].astype(str), sku_analytics_df['avg_unit_price']))
        desc_map = dict(zip(sku_analytics_df['ProductID'].astype(str), sku_analytics_df['Description']))
        
        bundle_candidates = []
        for _, row in rules.iterrows():
            ant_skus = list(row['antecedents'])
            con_skus = list(row['consequents'])
            
            if len(ant_skus) == 1 and len(con_skus) == 1:
                item_a = str(ant_skus[0])
                item_b = str(con_skus[0])
                
                class_a = abc_map.get(item_a, 'Unknown')
                class_b = abc_map.get(item_b, 'Unknown')
                
                # Check if pair contains 1 Anchor (A/B) and 1 Slow-Mover (C)
                is_bundle_pair = (
                    (class_a.startswith(('A', 'B')) and class_b.startswith('C')) or
                    (class_b.startswith(('A', 'B')) and class_a.startswith('C'))
                )
                
                anchor_sku = item_a if class_a.startswith(('A', 'B')) else item_b
                slow_sku = item_b if class_a.startswith(('A', 'B')) else item_a
                
                bundle_candidates.append({
                    'anchor_sku': anchor_sku,
                    'anchor_desc': desc_map.get(anchor_sku, anchor_sku),
                    'anchor_class': abc_map.get(anchor_sku, 'N/A'),
                    'slow_mover_sku': slow_sku,
                    'slow_mover_desc': desc_map.get(slow_sku, slow_sku),
                    'slow_mover_class': abc_map.get(slow_sku, 'N/A'),
                    'support': row['support'],
                    'confidence': row['confidence'],
                    'lift': row['lift'],
                    'anchor_price': price_map.get(anchor_sku, 0.0),
                    'slow_mover_price': price_map.get(slow_sku, 0.0),
                    'is_recommended_bundle': is_bundle_pair
                })
                
        bundles_df = pd.DataFrame(bundle_candidates)
        if not bundles_df.empty:
            bundles_df = bundles_df.sort_values(by=['is_recommended_bundle', 'lift'], ascending=[False, False])
        return bundles_df

if __name__ == "__main__":
    print("MarketBasketAnalyzer module initialized.")
