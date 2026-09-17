import os
import pandas as pd
import numpy as np

def generate_reviews_for_retail_data(data_dir: str):
    """
    Generates realistic customer text reviews mapped to real StockCodes from Online Retail dataset.
    Tags reviews with realistic sentiment signals (Sizing/Fit, Price/Value, Quality/Material).
    """
    retail_path = os.path.join(data_dir, "online_retail.csv")
    reviews_out_path = os.path.join(data_dir, "womens_clothing_reviews.csv")
    
    if not os.path.exists(retail_path):
        print(f"Error: {retail_path} not found.")
        return
        
    print("Reading real Online Retail dataset to extract product IDs...")
    df_retail = pd.read_csv(retail_path, encoding="ISO-8859-1", nrows=50000)
    df_clean = df_retail.dropna(subset=['StockCode', 'Description'])
    
    products = df_clean[['StockCode', 'Description']].drop_duplicates().head(250)
    
    np.random.seed(42)
    
    templates = {
        'positive': [
            "Love this product! The quality is fantastic and fits perfectly.",
            "Great purchase, looks amazing and very comfortable to wear.",
            "High quality fabric, beautiful color, would definitely buy again!",
            "Excellent item, super fast delivery and true to size.",
            "Absolutely gorgeous item! Exceeded my expectations."
        ],
        'sizing_fit': [
            "Way too small! Order at least two sizes up, the sleeves are very tight.",
            "Sizing is completely off. It fits loose around the waist but tight on shoulders.",
            "The fit is very awkward and much shorter than shown in photos.",
            "Runs very large and baggy. Had to return it for a smaller size."
        ],
        'price_value': [
            "Overpriced for what it is. The material feels cheap for this price point.",
            "Not worth the money. Very expensive for such basic quality.",
            "Felt ripped off. Cost too much for something that looks cheap.",
            "Overpriced item. You can find better quality for half the price."
        ],
        'quality_material': [
            "Disappointed with the material. Fabric is paper thin and see-through.",
            "Ripped along the seam after just one wash. Poor material quality.",
            "Color faded immediately after washing. Very rough fabric.",
            "Quality is poor, threads coming loose everywhere."
        ]
    }
    
    review_rows = []
    for idx, row in products.iterrows():
        p_id = str(row['StockCode'])
        p_desc = str(row['Description'])
        
        # Decide if this SKU has sentiment issues
        r_type = np.random.choice(['positive', 'sizing_fit', 'price_value', 'quality_material'], p=[0.55, 0.15, 0.15, 0.15])
        
        num_reviews = np.random.randint(3, 12)
        for _ in range(num_reviews):
            template_list = templates[r_type]
            text = np.random.choice(template_list)
            
            if r_type == 'positive':
                rating = np.random.choice([4, 5])
            else:
                rating = np.random.choice([1, 2, 3])
                
            review_rows.append({
                'clothing_id': p_id,
                'product_name': p_desc,
                'rating': rating,
                'review_text': text,
                'recommended_ind': 1 if rating >= 4 else 0,
                'positive_feedback_count': np.random.randint(0, 10),
                'class_name': 'General'
            })
            
    df_rev = pd.DataFrame(review_rows)
    df_rev.to_csv(reviews_out_path, index=False)
    print(f"Generated {len(df_rev):,} review records for {len(products)} real SKUs -> {reviews_out_path}")

if __name__ == "__main__":
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_directory = os.path.join(project_dir, "data", "raw")
    generate_reviews_for_retail_data(data_directory)
