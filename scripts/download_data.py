import os
import sys
import urllib.request

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
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print(f"✓ Downloaded {description} ({os.path.getsize(dest_path):,} bytes)")
        return True
    except Exception as e:
        print(f"❌ Download failed for {description}: {e}")
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
    
    return s1 and s2

if __name__ == "__main__":
    success = ensure_datasets_exist()
    if success:
        print("\n🎉 All raw benchmark datasets ready for execution!")
    else:
        sys.exit(1)
