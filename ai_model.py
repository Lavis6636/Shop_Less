# ai_model.py - AI for sales prediction and customer segmentation
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
from sklearn.metrics import silhouette_score
from numpy import array 
import os # Import os for file path management

# --- Configuration ---
MODEL_DIR = 'model'
PREDICTOR_FILENAME = 'sales_predictor.pkl'
SCALER_FILENAME = 'scaler.pkl' # We need a scaler file too!
FEATURE_FILENAME = 'features.json' # To store feature names needed for prediction

# Ensure the model directory exists
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

# Helper function to save/load feature names (as list of strings)
def save_features(feature_names, filename):
    import json
    path = os.path.join(MODEL_DIR, filename)
    with open(path, 'w') as f:
        json.dump(feature_names, f)

def load_features(filename):
    import json
    path = os.path.join(MODEL_DIR, filename)
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

class SalesPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = []
        self.is_trained = False
        self.load_model() # Attempt to load on initialization
        
    def generate_sample_data(self):
        # ... (rest of the generate_sample_data function remains unchanged) ...
        # (Using the version you provided in the prompt)
        np.random.seed(42)
        
        products = [
            {'name': 'iPhone X', 'base_price': 5000, 'category': 'flagship'},
            {'name': 'iPhone XS', 'base_price': 5200, 'category': 'flagship'},
            {'name': 'iPhone XS Max', 'base_price': 5500, 'category': 'flagship'},
            {'name': 'iPhone 11', 'base_price': 6000, 'category': 'flagship'},
            {'name': 'iPhone 11 Pro', 'base_price': 7000, 'category': 'premium'},
            {'name': 'iPhone 11 Pro Max', 'base_price': 8000, 'category': 'premium'},
            {'name': 'iPhone 12', 'base_price': 7000, 'category': 'premium'},
            {'name': 'iPhone 12 Pro', 'base_price': 8500, 'category': 'premium'},
            {'name': 'iPhone 12 Pro Max', 'base_price': 9000, 'category': 'premium'},
            {'name': 'iPhone 13', 'base_price': 8000, 'category': 'premium'},
            {'name': 'iPhone 13 Pro', 'base_price': 9500, 'category': 'luxury'},
            {'name': 'iPhone 13 Pro Max', 'base_price': 10000, 'category': 'luxury'},
            {'name': 'iPhone 14', 'base_price': 9000, 'category': 'premium'},
            {'name': 'iPhone 14 Pro', 'base_price': 11000, 'category': 'luxury'},
            {'name': 'iPhone 14 Pro Max', 'base_price': 12000, 'category': 'luxury'},
            {'name': 'iPhone 15', 'base_price': 10000, 'category': 'premium'},
            {'name': 'iPhone 15 Pro', 'base_price': 12500, 'category': 'luxury'},
            {'name': 'iPhone 15 Pro Max', 'base_price': 14000, 'category': 'luxury'},
        ]
        
        data = []
        start_date = datetime(2023, 11, 1) 
        
        for i in range(180): 
            date = start_date + timedelta(days=i)
            for product in products:
                day_of_week = date.weekday()
                month = date.month
                base_sales = np.random.poisson(3)
                
                if day_of_week >= 5: 
                    base_sales *= 1.5
                
                if month in [11, 12]: 
                    base_sales *= 2.0
                elif month in [6, 7]: 
                    base_sales *= 1.2
                
                price_multiplier = 1.0
                if product['category'] == 'luxury':
                    price_multiplier = 0.6
                elif product['category'] == 'premium':
                    price_multiplier = 0.8
                elif product['category'] == 'flagship':
                    price_multiplier = 1.2
                
                sales = max(1, int(base_sales * price_multiplier + np.random.normal(0, 1.5)))
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'product': product['name'],
                    'category': product['category'],
                    'price': product['base_price'],
                    'sales': sales,
                    'day_of_week': day_of_week,
                    'month': month,
                    'is_weekend': 1 if day_of_week >= 5 else 0,
                    'is_holiday_season': 1 if month in [11, 12] else 0,
                    'quarter': (month - 1) // 3 + 1
                })
        
        return pd.DataFrame(data)

    def prepare_features(self, df):
        # ... (rest of prepare_features remains unchanged) ...
        features_base = ['price', 'day_of_week', 'month', 'is_weekend', 'is_holiday_season', 'quarter']
        category_dummies = pd.get_dummies(df['category'], prefix='category')
        X = pd.concat([df[features_base], category_dummies], axis=1)
        y = df['sales']
        final_features = list(X.columns)
        return X, y, final_features

    def save_model(self):
        """Saves the trained model, scaler, and feature names."""
        if self.is_trained:
            print("💾 Saving Sales Predictor model assets...")
            joblib.dump(self.model, os.path.join(MODEL_DIR, PREDICTOR_FILENAME))
            joblib.dump(self.scaler, os.path.join(MODEL_DIR, SCALER_FILENAME))
            save_features(self.feature_names, FEATURE_FILENAME)
            print("✅ Sales Predictor saved.")

    def load_model(self):
        """Loads the trained model, scaler, and feature names."""
        try:
            print("⏳ Loading Sales Predictor model assets...")
            self.model = joblib.load(os.path.join(MODEL_DIR, PREDICTOR_FILENAME))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, SCALER_FILENAME))
            self.feature_names = load_features(FEATURE_FILENAME)
            
            if self.model and self.scaler and self.feature_names:
                self.is_trained = True
                print("✅ Sales Predictor successfully loaded!")
                return True
            return False
        except FileNotFoundError:
            print("⚠️ Sales Predictor files not found. Model needs training.")
            return False

    def train(self):
        """Train the sales prediction model"""
        # Check if the model is already trained and loaded
        if self.is_trained:
            print("🤖 Sales Predictor already trained and loaded.")
            return self.model.score(self.scaler.transform(self.prepare_features(self.generate_sample_data())[0].values), self.prepare_features(self.generate_sample_data())[1]) # Return a score

        # If not loaded, proceed with training
        print("🤖 Generating training data...")
        df = self.generate_sample_data()
        
        print("📊 Preparing features...")
        X, y, self.feature_names = self.prepare_features(df)
        
        if X.empty:
            print("🛑 Error: Training data is empty.")
            return 0.0

        print("🎯 Training Random Forest model...")
        self.scaler = StandardScaler() # Initialize scaler here if not loaded
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        X_scaled = self.scaler.fit_transform(X.values) 
        self.model.fit(X_scaled, y)
        
        self.is_trained = True
        
        train_score = self.model.score(X_scaled, y)
        print(f"✅ Model training completed! Training R² score: {train_score:.3f}")
        
        self.save_model() # Save the newly trained model
        return train_score
    
    def predict_sales(self, product_name, category, price, date):
        # ... (rest of predict_sales remains unchanged, but relies on self.is_trained) ...
        # Ensure that if the model is not trained (and could not be loaded), it calls self.train()
        if not self.is_trained:
            self.train() 
            
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d')
        
        features = {
            'price': price,
            'day_of_week': date.weekday(),
            'month': date.month,
            'is_weekend': 1 if date.weekday() >= 5 else 0,
            'is_holiday_season': 1 if date.month in [11, 12] else 0,
            'quarter': (date.month - 1) // 3 + 1
        }
        
        all_features_map = {}
        for feature in self.feature_names:
            all_features_map[feature] = features.get(feature, 0)
        
        for cat in ['flagship', 'premium', 'luxury']:
            key = f'category_{cat}'
            if key in all_features_map:
                all_features_map[key] = 1 if category == cat else 0
        
        if not self.feature_names:
            print("🛑 Error: Feature names not loaded/trained.")
            return 0
            
        X_pred = array([all_features_map[feature] for feature in self.feature_names])
        X_pred_scaled = self.scaler.transform(X_pred.reshape(1, -1)) 
        prediction = self.model.predict(X_pred_scaled)[0]
        
        return max(0, int(prediction))
    
    # ... (other methods like get_feature_importance and get_model_metrics remain) ...

# -------------------------------------------------------------
# Customer Segmenter modifications (similar logic)
# -------------------------------------------------------------

# FIX: Rename the Customer Segmenter filenames to be distinct
SEGMENTER_FILENAME = 'customer_segmenter.pkl'
SEGMENTER_SCALER_FILENAME = 'segmenter_scaler.pkl'


class CustomerSegmenter:
    def __init__(self):
        self.kmeans = None
        self.scaler = None
        self.is_trained = False
        self.customer_data = None
        self.load_model() # Attempt to load on initialization
    
    def save_model(self):
        """Saves the trained KMeans model and scaler."""
        if self.is_trained:
            print("💾 Saving Customer Segmenter assets...")
            joblib.dump(self.kmeans, os.path.join(MODEL_DIR, SEGMENTER_FILENAME))
            joblib.dump(self.scaler, os.path.join(MODEL_DIR, SEGMENTER_SCALER_FILENAME))
            print("✅ Customer Segmenter saved.")

    def load_model(self):
        """Loads the trained KMeans model and scaler."""
        try:
            print("⏳ Loading Customer Segmenter assets...")
            self.kmeans = joblib.load(os.path.join(MODEL_DIR, SEGMENTER_FILENAME))
            self.scaler = joblib.load(os.path.join(MODEL_DIR, SEGMENTER_SCALER_FILENAME))
            
            if self.kmeans and self.scaler:
                self.is_trained = True
                print("✅ Customer Segmenter successfully loaded!")
                return True
            return False
        except FileNotFoundError:
            print("⚠️ Customer Segmenter files not found. Model needs training.")
            return False

    def generate_customer_data(self, n_customers=1000):
        # ... (rest of generate_customer_data remains unchanged) ...
        # (Using the version you provided in the prompt)
        np.random.seed(42)
        data = []
        for i in range(n_customers):
            total_spent = np.random.gamma(2, 1000)
            purchase_frequency = np.random.poisson(3)
            avg_order_value = total_spent / (purchase_frequency if purchase_frequency > 0 else 1) 
            premium_ratio = np.random.beta(2, 5) 
            luxury_ratio = np.random.beta(1, 8) 
            data.append({
                'customer_id': i + 1,
                'total_spent': total_spent,
                'purchase_frequency': purchase_frequency,
                'avg_order_value': avg_order_value,
                'premium_ratio': premium_ratio,
                'luxury_ratio': luxury_ratio,
                'days_since_last_purchase': np.random.exponential(30)
            })
        return pd.DataFrame(data)

    def train(self):
        """Train customer segmentation model"""
        if self.is_trained:
            print("👥 Customer Segmenter already trained and loaded.")
            return self.kmeans.inertia_, 0.0 # Return existing inertia

        print("👥 Generating customer data...")
        df = self.generate_customer_data()
        
        features = ['total_spent', 'purchase_frequency', 'avg_order_value', 
                    'premium_ratio', 'luxury_ratio', 'days_since_last_purchase']
        X = df[features]
        
        if X.empty:
            print("🛑 Error: Customer data is empty.")
            return 0.0, 0.0

        print("🎯 Training customer segmentation model...")
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=4, random_state=42, n_init='auto')
        
        X_scaled = self.scaler.fit_transform(X.values) 
        self.kmeans.fit(X_scaled)
        
        self.is_trained = True
        df['segment'] = self.kmeans.labels_
        self.customer_data = df
        
        print("✅ Customer segmentation completed!")
        
        self.save_model() # Save the newly trained model
        
        inertia = self.kmeans.inertia_
        # ... (rest of inertia/silhouette calculation remains) ...
        silhouette = 0.0
        if len(np.unique(self.kmeans.labels_)) > 1 and len(X_scaled) > 1:
            silhouette = silhouette_score(X_scaled, self.kmeans.labels_)
            print(f"📈 Clustering Inertia: {inertia:.2f}, Silhouette Score: {silhouette:.3f}")
        else:
             print(f"📈 Clustering inertia: {inertia:.2f} (Silhouette score requires > 1 segment and samples)")
             
        return inertia, silhouette
    
    # ... (other methods like predict_segment and get_segment_stats remain) ...

# --- Initializing AI models ---
# Changed initialization to simply create the instances. 
# They will attempt to load on init, or train on first use if loading fails.
sales_predictor = SalesPredictor()
customer_segmenter = CustomerSegmenter()

print("🎉 AI Models initialized and ready (Loaded or will train on first prediction)! (Ignoring old automatic training)")