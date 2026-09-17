import pandas as pd
import numpy as np

class InventoryFinanceAnalytics:
    """
    Computes ABC Inventory Classification and Gross Margin Return on Inventory (GMROI).
    Classifies SKUs into A (High Velocity), B (Medium Velocity), C (Slow-Moving).
    """
    def __init__(self, a_quantile: float = 0.70, b_quantile: float = 0.90):
        self.a_quantile = a_quantile
        self.b_quantile = b_quantile

    def calculate_abc_classification(self, df_sku: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates Pareto ABC Classification based on cumulative revenue.
        """
        df = df_sku.copy()
        df = df.sort_values(by='total_revenue', ascending=False).reset_index(drop=True)
        
        total_rev = df['total_revenue'].sum()
        if total_rev > 0:
            df['cumulative_revenue'] = df['total_revenue'].cumsum()
            df['cum_rev_percent'] = df['cumulative_revenue'] / total_rev
        else:
            df['cum_rev_percent'] = 0.0

        def assign_abc(pct):
            if pct <= self.a_quantile:
                return 'A (High Velocity)'
            elif pct <= self.b_quantile:
                return 'B (Medium Velocity)'
            else:
                return 'C (Slow Moving)'

        df['abc_class'] = df['cum_rev_percent'].apply(assign_abc)
        return df

    def calculate_gmroi(self, df_sku: pd.DataFrame, annual_holding_cost_rate: float = 0.25) -> pd.DataFrame:
        """
        Calculates Gross Margin Return on Inventory (GMROI) and Holding Cost Burden.
        GMROI = Total Gross Margin ($) / Average Inventory Capital ($)
        """
        df = df_sku.copy()
        
        # Total Cost of Goods Sold (COGS)
        df['cogs'] = df['total_units_sold'] * df['avg_unit_cost']
        
        # Gross Margin ($)
        df['gross_margin_dollars'] = df['total_revenue'] - df['cogs']
        
        # Gross Margin %
        df['gross_margin_pct'] = np.where(df['total_revenue'] > 0, df['gross_margin_dollars'] / df['total_revenue'], 0.0)
        
        # Inventory Investment Capital ($)
        df['avg_inventory_capital'] = df['stock_on_hand'] * df['avg_unit_cost']
        
        # GMROI calculation
        df['gmroi'] = np.where(
            df['avg_inventory_capital'] > 0,
            df['gross_margin_dollars'] / df['avg_inventory_capital'],
            0.0
        ).round(2)
        
        # Holding Cost Burden ($ per year)
        df['holding_cost_annual'] = (df['avg_inventory_capital'] * annual_holding_cost_rate).round(2)
        
        # Stock Status Flag
        def assign_status(row):
            if row['abc_class'].startswith('C') and row['gmroi'] < 1.2:
                return 'Dead Stock (High Risk)'
            elif row['gmroi'] < 1.0:
                return 'Margin Eroding'
            elif row['abc_class'].startswith('A'):
                return 'Star Anchor SKU'
            else:
                return 'Healthy Inventory'
                
        df['inventory_status'] = df.apply(assign_status, axis=1)
        return df

if __name__ == "__main__":
    sample_data = pd.DataFrame({
        'ProductID': ['P1', 'P2', 'P3'],
        'Description': ['Item A', 'Item B', 'Item C'],
        'total_units_sold': [100, 20, 2],
        'total_revenue': [5000.0, 1000.0, 100.0],
        'avg_unit_price': [50.0, 50.0, 50.0],
        'avg_unit_cost': [20.0, 25.0, 30.0],
        'stock_on_hand': [50, 100, 200]
    })
    ifa = InventoryFinanceAnalytics()
    abc_df = ifa.calculate_abc_classification(sample_data)
    fin_df = ifa.calculate_gmroi(abc_df)
    print(fin_df[['ProductID', 'abc_class', 'gmroi', 'inventory_status']])
