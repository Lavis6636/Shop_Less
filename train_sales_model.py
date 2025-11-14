# train_sales_model.py
"""
Shop-Less AI: Sales Prediction Model Trainer
- Uses PRODUCT_CATALOG for synthetic dataset
- Trains RandomForestRegressor
- Saves model and encoders for Flask integration
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# -----------------------------
# Product Catalog
# -----------------------------
PRODUCT_CATALOG = [
    {'sku': 'ipx', 'name': 'iPhone X', 'series': 'X', 'base_price': 5000.00},
    {'sku': 'ipxs', 'name': 'iPhone XS', 'series': 'X', 'base_price': 5200.00},
    {'sku': 'ipxsmax', 'name': 'iPhone XS Max', 'series': 'X', 'base_price': 5500.00},
    {'sku': 'ip11', 'name': 'iPhone 11', 'series': '11', 'base_price': 6000.00},
    {'sku': 'ip11pro', 'name': 'iPhone 11 Pro', 'series': '11', 'base_price': 7000.00},
    {'sku': 'ip11promax', 'name': 'iPhone 11 Pro Max', 'series': '11', 'base_price': 8000.00},
    {'sku': 'ip12', 'name': 'iPhone 12', 'series': '12', 'base_price': 7000.00},
    {'sku': 'ip12mini', 'name': 'iPhone 12 mini', 'series': '12', 'base_price': 6800.00},
    {'sku': 'ip12pro', 'name': 'iPhone 12 Pro', 'series': '12', 'base_price': 8500.00},
    {'sku': 'ip12promax', 'name': 'iPhone 12 Pro Max', 'series': '12', 'base_price': 9000.00},
    {'sku': 'ip13', 'name': 'iPhone 13', 'series': '13', 'base_price': 8000.00},
    {'sku': 'ip13mini', 'name': 'iPhone 13 mini', 'series': '13', 'base_price': 7800.00},
    {'sku': 'ip13pro', 'name': 'iPhone 13 Pro', 'series': '13', 'base_price': 9500.00},
    {'sku': 'ip13promax', 'name': 'iPhone 13 Pro Max', 'series': '13', 'base_price': 10000.00},
    {'sku': 'ip14', 'name': 'iPhone 14', 'series': '14', 'base_price': 9000.00},
    {'sku': 'ip14plus', 'name': 'iPhone 14 Plus', 'series': '14', 'base_price': 9200.00},
    {'sku': 'ip14pro', 'name': 'iPhone 14 Pro', 'series': '14', 'base_price': 11000.00},
    {'sku': 'ip14promax', 'name': 'iPhone 14 Pro Max', 'series': '14', 'base_price': 12000.00},
    {'sku': 'ip15', 'name': 'iPhone 15', 'series': '15', 'base_price': 10000.00},
    {'sku': 'ip15plus', 'name': 'iPhone 15 Plus', 'series': '15', 'base_price': 10200.00},
    {'sku': 'ip15pro', 'name': 'iPhone 15 Pro', 'series': '15', 'base_price': 12500.00},
    {'sku': 'ip15promax', 'name': 'iPhone 15 Pro Max', 'series': '15', 'base_price': 14000.00},
    {'sku': 'ip16', 'name': 'iPhone 16', 'series': '16', 'base_price': 11000.00,},
    {'sku': 'ip16pro', 'name': 'iPhone 16 Pro', 'series': '16', 'base_price': 14000.00,},
    {'sku': 'ip16promax', 'name': 'iPhone 16 Pro Max', 'series': '16', 'base_price': 16000.00,},
    {'sku': 'ip17', 'name': 'iPhone 17', 'series': '17', 'base_price': 12000.00,},
    {'sku': 'ip17pro', 'name': 'iPhone 17 Pro', 'series': '17', 'base_price': 15500.00,},
    {'sku': 'ip17promax', 'name': 'iPhone 17 Pro Max', 'series': '17', 'base_price': 18000.00,},
]

# -----------------------------
# Step 1: Generate Synthetic Dataset
# -----------------------------
dates = pd.date_range(start='2025-01-01', periods=120)  # 4 months
data = []

np.random.seed(42)  # reproducibility

for date in dates:
    for product in PRODUCT_CATALOG:
        price = product['base_price']
        rating = round(np.random.uniform(3.0, 5.0), 1)
        reviews = np.random.randint(10, 500)
        stock = np.random.randint(5, 50)
        daily_sales = max(0, int(np.random.normal(loc=20, scale=5)))  # daily sales
        data.append([
            product['name'],
            product['series'],
            price,
            rating,
            reviews,
            stock,
            daily_sales,
            date
        ])

df = pd.DataFrame(data, columns=[
    'product_name', 'series', 'price', 'rating', 'reviews_count', 'stock', 'daily_sales', 'date'
])

os.makedirs('data', exist_ok=True)
df.to_csv('data/sales_dataset.csv', index=False)
print("Synthetic dataset saved to data/sales_dataset.csv")

# -----------------------------
# Step 2: Encode categorical features
# -----------------------------
le_product = LabelEncoder()
df['product_enc'] = le_product.fit_transform(df['product_name'])

le_series = LabelEncoder()
df['series_enc'] = le_series.fit_transform(df['series'])

X = df[['product_enc', 'series_enc', 'price', 'rating', 'reviews_count', 'stock']]
y = df['daily_sales']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# Step 3: Train Model
# -----------------------------
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

model = RandomForestRegressor(n_estimators=150, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Calculate R² and RMSE
r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"Model trained! R²: {r2:.3f}, RMSE: {rmse:.2f}")

# -----------------------------
# Step 4: Save Model & Encoders
# -----------------------------
os.makedirs('model', exist_ok=True)
joblib.dump(model, 'model/sales_predictor.pkl')
joblib.dump(le_product, 'model/product_encoder.pkl')
joblib.dump(le_series, 'model/series_encoder.pkl')
print("Model and encoders saved to model/ folder")
