import os
import zlib
import pandas as pd
import numpy as np

NON_PRODUCT_CODES = {
    'POST', 'DOT', 'M', 'D', 'S', 'B', 'C2', 'CRUK', 'AMAZONFEE',
    'BANK CHARGES', 'PADS', 'ADJUST', 'ADJUST2', 'TEST001', 'TEST002',
}

class ETLPipeline:
    """
    ETL Pipeline for Retail Transaction Logs and Customer Reviews.
    Ingests raw sales records and review datasets, performing data cleaning,
    standardization, SKU-level aggregation, and deterministic feature engineering.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.retail_path = os.path.join(data_dir, "online_retail.csv")
        self.reviews_path = os.path.join(data_dir, "womens_clothing_reviews.csv")
        
    def load_raw_data(self):
        """Loads raw CSV files from disk."""
        df_retail = None
        df_reviews = None
        
        if os.path.exists(self.retail_path):
            df_retail = pd.read_csv(self.retail_path, encoding="ISO-8859-1")
        else:
            raise FileNotFoundError(f"Missing dataset at {self.retail_path}")
            
        if os.path.exists(self.reviews_path):
            df_reviews = pd.read_csv(self.reviews_path)
            
        return df_retail, df_reviews

    def clean_retail_data(self, df_retail: pd.DataFrame) -> pd.DataFrame:
        """Cleans sales transaction logs."""
        df = df_retail.copy()
        df.columns = [c.strip() for c in df.columns]
        
        # Filter cancelled orders and standardize column names
        if 'InvoiceNo' in df.columns:
            df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
        elif 'Invoice' in df.columns:
            df = df[~df['Invoice'].astype(str).str.startswith('C')]
            df.rename(columns={'Invoice': 'InvoiceNo'}, inplace=True)
            
        if 'Price' in df.columns and 'UnitPrice' not in df.columns:
            df.rename(columns={'Price': 'UnitPrice'}, inplace=True)
            
        if 'StockCode' in df.columns and 'ProductID' not in df.columns:
            df.rename(columns={'StockCode': 'ProductID'}, inplace=True)

        # Filter valid transactions with positive quantity and unit price
        df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]

        # Drop non-merchandise StockCodes (postage, carriage, fees, manual
        # adjustments, gift vouchers). They are ledger lines, not sellable
        # products: left in, "DOTCOM POSTAGE" becomes the top-revenue A-class
        # SKU and gets paired with real products as a bundle anchor.
        code = df['ProductID'].astype(str).str.strip().str.upper()
        df = df[~(code.isin(NON_PRODUCT_CODES) | code.str.startswith('GIFT_'))]

        df['LineRevenue'] = df['Quantity'] * df['UnitPrice']
        
        if 'InvoiceDate' in df.columns:
            df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='mixed', errors='coerce')
            
        return df

    def aggregate_sku_level_metrics(self, df_retail: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregates transaction logs into SKU-level metrics.
        Groups strictly by ProductID to prevent description duplicates.
        Generates deterministic cost and inventory stock based on SKU ID hash.
        """
        sku_df = df_retail.groupby('ProductID').agg(
            Description=('Description', lambda x: x.dropna().iloc[0] if not x.dropna().empty else 'Item ' + str(x.name)),
            total_units_sold=('Quantity', 'sum'),
            total_revenue=('LineRevenue', 'sum'),
            order_frequency=('InvoiceNo', 'nunique'),
            avg_unit_price=('UnitPrice', 'mean'),
            last_sold_date=('InvoiceDate', 'max')
        ).reset_index()
        
        # Calculate recency (days since last sale)
        max_date = sku_df['last_sold_date'].max()
        sku_df['days_since_last_sale'] = (max_date - sku_df['last_sold_date']).dt.days.fillna(30).astype(int)
        
        # Deterministic wholesale unit cost (assumes 40% - 60% gross margin based on ProductID CRC32)
        sku_df['cost_seed'] = sku_df['ProductID'].apply(lambda x: (zlib.crc32(str(x).encode('utf-8')) % 1000) / 1000.0)
        sku_df['avg_unit_cost'] = (sku_df['avg_unit_price'] * (1.0 - (0.40 + 0.20 * sku_df['cost_seed']))).round(2)
        
        # Annual dataset active period
        min_date = df_retail['InvoiceDate'].min() if 'InvoiceDate' in df_retail.columns else sku_df['last_sold_date'].min()
        total_days = max(1, (max_date - min_date).days)
        daily_sales = sku_df['total_units_sold'] / total_days
        
        # Initial revenue share for supply chain stock targets (70-20-10 Pareto)
        rev_sorted = sku_df.sort_values(by='total_revenue', ascending=False)
        cum_rev = rev_sorted['total_revenue'].cumsum() / rev_sorted['total_revenue'].sum()
        abc_pre = np.where(cum_rev <= 0.70, 'A', np.where(cum_rev <= 0.90, 'B', 'C'))
        sku_df.loc[rev_sorted.index, 'temp_abc'] = abc_pre

        # Supply chain Days of Supply (DOS) calibration:
        # A-tier: Lean 30-45 DOS (high turnover)
        # B-tier: Balanced 50-75 DOS
        # C-tier: Bloated 120-220 DOS with aging penalty (sluggish turnover, clearance candidates)
        dos = np.where(
            sku_df['temp_abc'] == 'A',
            35 + 15 * sku_df['cost_seed'],
            np.where(
                sku_df['temp_abc'] == 'B',
                55 + 20 * sku_df['cost_seed'],
                130 + 80 * sku_df['cost_seed'] + (sku_df['days_since_last_sale'] * 0.4)
            )
        )
        sku_df['days_of_supply'] = dos.round(0).astype(int)
        sku_df['stock_on_hand'] = np.maximum(5, (daily_sales * dos).round(0)).astype(int)
        sku_df['inventory_age_days'] = sku_df['days_since_last_sale'] + (15 + (45 * sku_df['cost_seed'])).astype(int)
        
        sku_df.drop(columns=['cost_seed', 'temp_abc'], inplace=True)
        return sku_df

    def clean_reviews_data(self, df_reviews: pd.DataFrame) -> pd.DataFrame:
        """Cleans customer text reviews dataset."""
        if df_reviews is None or df_reviews.empty:
            return pd.DataFrame()
            
        df = df_reviews.copy()
        df.columns = [c.strip().replace(' ', '_').lower() for c in df.columns]
        
        review_col = 'review_text' if 'review_text' in df.columns else 'text'
        df['clean_review'] = df[review_col].fillna("").astype(str) if review_col in df.columns else ""
        
        rating_col = 'rating' if 'rating' in df.columns else 'stars'
        df['rating'] = pd.to_numeric(df[rating_col], errors='coerce').fillna(3.0) if rating_col in df.columns else 3.0
            
        return df
