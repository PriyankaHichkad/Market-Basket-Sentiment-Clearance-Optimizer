import os
import pandas as pd
import numpy as np

class ETLPipeline:
    """
    ETL Pipeline for Real-World Retail Transaction & Customer Review Data.
    Ingests Online Retail transactions and Women's Clothing Reviews,
    performing cleaning, aggregation, and feature engineering.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.retail_path = os.path.join(data_dir, "online_retail.csv")
        self.reviews_path = os.path.join(data_dir, "womens_clothing_reviews.csv")
        
    def load_raw_data(self):
        """Loads raw CSV files from disk."""
        print("Loading raw datasets...")
        df_retail = None
        df_reviews = None
        
        if os.path.exists(self.retail_path):
            df_retail = pd.read_csv(self.retail_path, encoding="ISO-8859-1")
            print(f"Loaded Online Retail: {len(df_retail):,} rows")
        else:
            raise FileNotFoundError(f"Missing {self.retail_path}")
            
        if os.path.exists(self.reviews_path):
            df_reviews = pd.read_csv(self.reviews_path)
            print(f"Loaded Women's Clothing Reviews: {len(df_reviews):,} rows")
        else:
            print(f"Warning: {self.reviews_path} not found.")
            
        return df_retail, df_reviews

    def clean_retail_data(self, df_retail: pd.DataFrame) -> pd.DataFrame:
        """Cleans sales transaction logs."""
        df = df_retail.copy()
        
        # Standardize column names if needed
        df.columns = [c.strip() for c in df.columns]
        
        # Remove null Customer IDs, cancelled orders (InvoiceNo starting with 'C'), negative/zero quantities & prices
        if 'InvoiceNo' in df.columns:
            df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
        elif 'Invoice' in df.columns:
            df = df[~df['Invoice'].astype(str).str.startswith('C')]
            df.rename(columns={'Invoice': 'InvoiceNo'}, inplace=True)
            
        if 'Price' in df.columns and 'UnitPrice' not in df.columns:
            df.rename(columns={'Price': 'UnitPrice'}, inplace=True)
            
        if 'StockCode' in df.columns and 'ProductID' not in df.columns:
            df.rename(columns={'StockCode': 'ProductID'}, inplace=True)

        # Filter positive quantity and unit price
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
        
        # Line item revenue
        df['LineRevenue'] = df['Quantity'] * df['UnitPrice']
        
        # Parse dates
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
            
        print(f"Cleaned Online Retail: {len(df):,} valid line items")
        return df

    def aggregate_sku_level_metrics(self, df_retail: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates transaction logs into SKU-level metrics:
        Total Quantity Sold, Total Revenue, Order Count, Unit Price, Days in Inventory, Cost, Stock.
        """
        sku_df = df_retail.groupby(['ProductID', 'Description']).agg(
            total_units_sold=('Quantity', 'sum'),
            total_revenue=('LineRevenue', 'sum'),
            order_frequency=('InvoiceNo', 'nunique'),
            avg_unit_price=('UnitPrice', 'mean'),
            last_sold_date=('InvoiceDate', 'max'),
            first_sold_date=('InvoiceDate', 'min')
        ).reset_index()
        
        # Estimate Unit Cost assuming average retail gross margin of ~50% with realistic variance
        np.random.seed(42)
        margin_factors = np.random.uniform(0.40, 0.60, len(sku_df))
        sku_df['avg_unit_cost'] = (sku_df['avg_unit_price'] * (1 - margin_factors)).round(2)
        
        # Estimate Stock On Hand based on historical order frequency and sales velocity
        # Slow-moving items tend to have excess stock sitting on hand
        max_date = sku_df['last_sold_date'].max()
        sku_df['days_since_last_sale'] = (max_date - sku_df['last_sold_date']).dt.days
        
        # Estimate Stock On Hand: high for slow-movers, balanced for fast-movers
        velocity_daily = sku_df['total_units_sold'] / (sku_df['days_since_last_sale'] + 30)
        sku_df['stock_on_hand'] = (velocity_daily * np.random.uniform(30, 120, len(sku_df))).astype(int) + 10
        
        # Days in Inventory / Inventory Ageing
        sku_df['inventory_age_days'] = sku_df['days_since_last_sale'] + np.random.randint(15, 90, len(sku_df))
        
        return sku_df

    def clean_reviews_data(self, df_reviews: pd.DataFrame) -> pd.DataFrame:
        """Cleans real-world customer text reviews dataset."""
        if df_reviews is None or df_reviews.empty:
            return pd.DataFrame()
            
        df = df_reviews.copy()
        
        # Standardize column names
        df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
        
        # Standardize text field
        review_col = 'review_text' if 'review_text' in df.columns else 'text'
        if review_col in df.columns:
            df['clean_review'] = df[review_col].fillna("").astype(str)
        else:
            df['clean_review'] = ""
            
        rating_col = 'rating' if 'rating' in df.columns else 'stars'
        if rating_col in df.columns:
            df['rating'] = pd.to_numeric(df[rating_col], errors='coerce').fillna(3.0)
            
        print(f"Cleaned Reviews: {len(df):,} reviews")
        return df

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_dir, "data", "raw")
    etl = ETLPipeline(raw_dir)
    try:
        r, rev = etl.load_raw_data()
        clean_r = etl.clean_retail_data(r)
        sku_m = etl.aggregate_sku_level_metrics(clean_r)
        print(sku_m.head())
    except Exception as e:
        print(f"ETL Execution info: {e}")
