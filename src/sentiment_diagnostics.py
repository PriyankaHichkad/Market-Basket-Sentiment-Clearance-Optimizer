import pandas as pd
import numpy as np
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer

class SentimentDiagnostics:
    """
    Structured 3-Step NLP Analytical Workflow:
    - Step 1: Preprocessing & VADER Polarity Scoring (Quantifies how negative/positive text is).
    - Step 2: Traditional NLP Feature Extraction (TF-IDF + N-grams to answer WHY text is negative).
    - Step 3: Business Insights & Category Aggregation (Maps findings to SKU & Merchandising Category level).
    """
    def __init__(self, issue_categories: dict = None):
        self.analyzer = SentimentIntensityAnalyzer()
        if issue_categories is None:
            self.issue_categories = {
                'Sizing & Fit Flaw': ['small', 'large', 'fit', 'tight', 'loose', 'size', 'sizing', 'short', 'long', 'waist', 'sleeve'],
                'Price & Overpriced': ['expensive', 'overpriced', 'price', 'cost', 'worth', 'money', 'cheap', 'value'],
                'Quality & Fabric Flaw': ['quality', 'fabric', 'material', 'thin', 'ripped', 'tear', 'color', 'washed', 'shrink', 'rough', 'poor']
            }
        else:
            self.issue_categories = issue_categories

    # -------------------------------------------------------------
    # STEP 1: Preprocessing & VADER Sentiment Scoring
    # -------------------------------------------------------------
    def step1_vader_preprocessing(self, df_reviews: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 1: Cleans review text and calculates VADER sentiment scores.
        Outputs: vader_compound, vader_neg, vader_pos, sentiment_label
        """
        df = df_reviews.copy()
        text_col = 'clean_review' if 'clean_review' in df.columns else 'review_text'
        
        if text_col not in df.columns:
            print("No review text column found.")
            return df

        print("STEP 1: Running VADER Sentiment Analysis...")
        
        def run_vader(text):
            if not text or not isinstance(text, str):
                return {'compound': 0.0, 'neg': 0.0, 'pos': 0.0, 'sentiment_label': 'Neutral'}
            scores = self.analyzer.polarity_scores(text)
            comp = scores['compound']
            if comp >= 0.05:
                label = 'Positive'
            elif comp <= -0.05:
                label = 'Negative'
            else:
                label = 'Neutral'
            scores['sentiment_label'] = label
            return scores

        vader_results = df[text_col].apply(run_vader)
        
        df['vader_compound'] = [r['compound'] for r in vader_results]
        df['vader_neg'] = [r['neg'] for r in vader_results]
        df['vader_pos'] = [r['pos'] for r in vader_results]
        df['sentiment_label'] = [r['sentiment_label'] for r in vader_results]
        
        # Add rule-based root cause categorization
        df['root_cause_category'] = df.apply(
            lambda row: self.classify_root_cause(row[text_col]) if row['vader_compound'] < 0.05 else 'Positive Experience',
            axis=1
        )
        
        return df

    def classify_root_cause(self, text: str) -> str:
        """Classifies negative review text into root cause category."""
        if not text or not isinstance(text, str):
            return 'General Feedback'
        text_clean = text.lower()
        matches = {}
        for category, keywords in self.issue_categories.items():
            count = sum(1 for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', text_clean))
            if count > 0:
                matches[category] = count
        return max(matches, key=matches.get) if matches else 'General Dissatisfaction'

    # -------------------------------------------------------------
    # STEP 2: Traditional NLP Feature Extraction (TF-IDF & N-grams)
    # -------------------------------------------------------------
    def step2_tfidf_ngram_extraction(self, df_processed_reviews: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """
        STEP 2: Applies TF-IDF & Bi-gram / Tri-gram extraction on negative reviews
        to uncover the exact underlying phrases explaining 'WHY' reviews are negative.
        """
        text_col = 'clean_review' if 'clean_review' in df_processed_reviews.columns else 'review_text'
        neg_reviews = df_processed_reviews[df_processed_reviews['sentiment_label'] == 'Negative'][text_col].dropna()
        
        if neg_reviews.empty:
            print("No negative reviews available for N-gram extraction.")
            return pd.DataFrame()

        print(f"STEP 2: Extracting TF-IDF Bi-grams & Tri-grams across {len(neg_reviews):,} negative reviews...")
        
        vectorizer = TfidfVectorizer(
            ngram_range=(2, 3),
            stop_words='english',
            min_df=2,
            max_features=top_n
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(neg_reviews)
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.sum(axis=0).A1
            
            ngram_df = pd.DataFrame({
                'ngram_phrase': feature_names,
                'tfidf_score': scores
            }).sort_values(by='tfidf_score', ascending=False).reset_index(drop=True)
            
            return ngram_df
        except Exception as e:
            print(f"N-gram extraction warning: {e}")
            return pd.DataFrame()

    # -------------------------------------------------------------
    # STEP 3: Business Insights & Category Aggregation
    # -------------------------------------------------------------
    def step3_aggregate_business_insights(self, df_processed_reviews: pd.DataFrame) -> pd.DataFrame:
        """
        STEP 3: Aggregates VADER scores, sentiment proportions, and top root causes
        by SKU and Category level for Merchandising Decision-Making.
        """
        if 'clothing_id' in df_processed_reviews.columns:
            product_col = 'clothing_id'
        elif 'product_id' in df_processed_reviews.columns:
            product_col = 'product_id'
        else:
            print("No product ID column in reviews for aggregation.")
            return pd.DataFrame()
            
        print("STEP 3: Aggregating Sentiment & Root Causes to Product SKU Level...")
        summary = df_processed_reviews.groupby(product_col).agg(
            total_reviews=(product_col, 'count'),
            avg_rating=('rating', 'mean'),
            avg_vader_compound=('vader_compound', 'mean'),
            negative_review_count=('sentiment_label', lambda x: (x == 'Negative').sum()),
            top_root_cause=('root_cause_category', lambda x: x[x != 'Positive Experience'].mode()[0] if not x[x != 'Positive Experience'].empty else 'No Major Issue')
        ).reset_index()
        
        summary['negative_review_pct'] = (summary['negative_review_count'] / summary['total_reviews']).round(2)
        summary['avg_vader_compound'] = summary['avg_vader_compound'].round(3)
        return summary

    def process_reviews_dataframe(self, df_reviews: pd.DataFrame) -> pd.DataFrame:
        """Helper to run Step 1 Preprocessing."""
        return self.step1_vader_preprocessing(df_reviews)

    def aggregate_sku_sentiment(self, df_processed_reviews: pd.DataFrame) -> pd.DataFrame:
        """Helper to run Step 3 Aggregation."""
        return self.step3_aggregate_business_insights(df_processed_reviews)

if __name__ == "__main__":
    sd = SentimentDiagnostics()
    sample_df = pd.DataFrame({
        'clean_review': [
            "The dress is way too small and tight on shoulders.",
            "Material is paper thin and fabric ripped after one wash!",
            "Completely overpriced for basic cheap quality.",
            "Love this jacket! High quality and fits great."
        ],
        'rating': [2, 1, 2, 5],
        'clothing_id': ['P101', 'P101', 'P102', 'P103']
    })
    s1 = sd.step1_vader_preprocessing(sample_df)
    s2 = sd.step2_tfidf_ngram_extraction(s1)
    s3 = sd.step3_aggregate_business_insights(s1)
    
    print("\n--- STEP 1 OUTCOME ---")
    print(s1[['clean_review', 'vader_compound', 'sentiment_label', 'root_cause_category']])
    print("\n--- STEP 2 N-GRAM OUTCOME ---")
    print(s2)
    print("\n--- STEP 3 BUSINESS AGGREGATION OUTCOME ---")
    print(s3)
