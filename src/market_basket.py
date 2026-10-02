import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules

class MarketBasketAnalyzer:
    """
    Market Basket Analysis Engine using Apriori Algorithm.
    Mines co-purchasing patterns and association rules from transaction logs
    to identify anchor products to pair with slow-moving inventory.
    """
    def __init__(self, min_support: float = 0.003, min_confidence: float = 0.05, min_lift: float = 1.05):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift

    def prepare_basket_matrix(self, df_retail: pd.DataFrame, sku_analytics_df: pd.DataFrame = None, max_items: int = 100) -> pd.DataFrame:
        """
        Transforms transaction logs into a binary One-Hot Encoded basket matrix.
        Ensures representation of both high-velocity anchors (A/B) and clearance candidates (C).
        """
        if sku_analytics_df is not None and not sku_analytics_df.empty and 'abc_class' in sku_analytics_df.columns:
            a_skus = sku_analytics_df[sku_analytics_df['abc_class'].str.startswith(('A', 'B'))]['ProductID'].head(70)
            c_skus = sku_analytics_df[sku_analytics_df['abc_class'].str.startswith('C')]['ProductID'].head(50)
            selected_skus = set(a_skus).union(set(c_skus))
            df_filtered = df_retail[df_retail['ProductID'].isin(selected_skus)]
        else:
            top_products = df_retail['ProductID'].value_counts().head(max_items).index
            df_filtered = df_retail[df_retail['ProductID'].isin(top_products)]
        
        basket = (df_filtered.groupby(['InvoiceNo', 'ProductID'])['Quantity']
                  .sum().unstack().reset_index().fillna(0)
                  .set_index('InvoiceNo'))
                  
        basket_binary = (basket > 0)
        return basket_binary

    def run_apriori(self, basket_matrix: pd.DataFrame) -> pd.DataFrame:
        """Runs Apriori algorithm to find frequent itemsets."""
        if basket_matrix.empty:
            return pd.DataFrame()
            
        frequent_itemsets = apriori(basket_matrix, min_support=self.min_support, use_colnames=True)
        return frequent_itemsets

    def generate_association_rules(self, frequent_itemsets: pd.DataFrame) -> pd.DataFrame:
        """Generates association rules from frequent itemsets."""
        if frequent_itemsets.empty:
            return pd.DataFrame()

        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=self.min_confidence)
        rules = rules[rules['lift'] >= self.min_lift].sort_values(by='lift', ascending=False).reset_index(drop=True)
        
        rules['antecedents_str'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        rules['consequents_str'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
        
        return rules

    def find_bundle_recommendations(self, rules: pd.DataFrame, sku_analytics_df: pd.DataFrame) -> pd.DataFrame:
        """
        Pairs slow-moving C-Class products with high-demand A/B-Class products based on mined rules.
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
                
                # Identify pairs containing 1 Anchor (A/B) and 1 Slow-Mover (C)
                is_bundle_pair = (
                    (class_a.startswith(('A', 'B')) and class_b.startswith('C')) or
                    (class_b.startswith(('A', 'B')) and class_a.startswith('C'))
                )
                
                if is_bundle_pair:
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
                        'lift': row['lift']
                    })
                    
        return pd.DataFrame(bundle_candidates).drop_duplicates(subset=['anchor_sku', 'slow_mover_sku'])
