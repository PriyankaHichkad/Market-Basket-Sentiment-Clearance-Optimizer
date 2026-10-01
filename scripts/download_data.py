import os
import sys
import urllib.request
import pandas as pd
import numpy as np

def generate_fallback_datasets(data_dir: str):
    """Generates synthetic benchmark datasets if external download fails or times out."""
    os.makedirs(data_dir, exist_ok=True)
    retail_path = os.path.join(data_dir, "online_retail.csv")
    reviews_path = os.path.join(data_dir, "womens_clothing_reviews.csv")
    
    if not os.path.exists(retail_path) or os.path.getsize(retail_path) < 1000:
        print("Generating fallback Online Retail benchmark dataset...")
        np.random.seed(42)
        skus = [f"SKU_{i:04d}" for i in range(1, 101)]
        descs = [f"Product {i} Premium Retail Item" for i in range(1, 101)]
        sku_map = dict(zip(skus, descs))
        
        rows = []
        for inv in range(10000, 15000):
            inv_no = f"53{inv}"
            num_items = np.random.randint(1, 6)
            chosen_skus = np.random.choice(skus, size=num_items, replace=False)
            for sku in chosen_skus:
                rows.append({
                    'InvoiceNo': inv_no,
                    'StockCode': sku,
                    'Description': sku_map[sku],
                    'Quantity': np.random.randint(1, 12),
                    'InvoiceDate': '2021-12-01 12:00:00',
                    'UnitPrice': round(np.random.uniform(5.0, 95.0), 2),
                    'CustomerID': np.random.randint(12000, 18000),
                    'Country': 'United Kingdom'
                })
        pd.DataFrame(rows).to_csv(retail_path, index=False)
        print(f"Generated fallback {retail_path}")
        
    if not os.path.exists(reviews_path) or os.path.getsize(reviews_path) < 1000:
        print("Generating fallback Clothing Reviews benchmark dataset...")
        rev_rows = [
            {'Clothing ID': 101, 'Age': 32, 'Title': 'Runs very small', 'Review Text': 'The fit is way too small and tight. Sizing flaw.', 'Rating': 2, 'Recommended IND': 0, 'Department Name': 'Dresses'},
            {'Clothing ID': 102, 'Age': 45, 'Title': 'Overpriced fabric', 'Review Text': 'Material is thin and overpriced for the cost.', 'Rating': 2, 'Recommended IND': 0, 'Department Name': 'Tops'},
            {'Clothing ID': 103, 'Age': 28, 'Title': 'Love this dress', 'Review Text': 'Fits perfectly, high quality material and great value.', 'Rating': 5, 'Recommended IND': 1, 'Department Name': 'Dresses'}
        ] * 100
        pd.DataFrame(rev_rows).to_csv(reviews_path, index=False)
        print(f"Generated fallback {reviews_path}")

def download_file(url: str, dest_path: str, description: str):
    """Downloads a dataset file with progress updates if missing or invalid."""
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 500000:
        print(f"✓ {description} already exists at {dest_path} ({os.path.getsize(dest_path):,} bytes)")
        return True
        
    print(f"Downloading {description} from {url}...")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response, open(dest_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"✓ Downloaded {description} ({os.path.getsize(dest_path):,} bytes)")
        return True
    except Exception as e:
        print(f"Download info for {description}: {e}")
        return False

def ensure_datasets_exist(data_dir: str = None):
    """Ensures raw datasets exist locally in data/raw/."""
    if data_dir is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(project_root, 'data', 'raw')
        
    os.makedirs(data_dir, exist_ok=True)
    
    retail_url = "https://raw.githubusercontent.com/guipsamora/pandas_exercises/master/07_Visualization/Online_Retail/Online_Retail.csv"
    reviews_url = "https://raw.githubusercontent.com/AFAgarap/ecommerce-reviews-analysis/master/Womens%20Clothing%20E-Commerce%20Reviews.csv"
    
    retail_path = os.path.join(data_dir, "online_retail.csv")
    reviews_path = os.path.join(data_dir, "womens_clothing_reviews.csv")
    
    s1 = download_file(retail_url, retail_path, "Online Retail Transaction Dataset (UCI)")
    s2 = download_file(reviews_url, reviews_path, "Women's Clothing E-Commerce Reviews Dataset (Kaggle)")
    
    if not (s1 and s2):
        generate_fallback_datasets(data_dir)
        
    return True

if __name__ == "__main__":
    success = ensure_datasets_exist()
    if success:
        print("\nAll raw benchmark datasets ready for execution!")
    else:
        sys.exit(1)

