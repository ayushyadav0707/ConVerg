import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def parse_sqft(x):
    try:
        x = str(x)
        if '-' in x:
            tokens = x.split('-')
            return (float(tokens[0].strip()) + float(tokens[1].strip())) / 2
        return float(x.replace('Sq. Meter','').replace('Sq. Yards','').replace('Acres','').replace('Guntha','').replace('Grounds','').replace('Cents','').strip())
    except:
        return np.nan

def load_and_preprocess(filepath):
    print("Loading data...")
    df = pd.read_csv(filepath)
    
    # 1. Clean features
    df['total_sqft_num'] = df['total_sqft'].apply(parse_sqft)
    
    def parse_bhk(x):
        if pd.isna(x): return 2.0
        try: return float(str(x).split(' ')[0])
        except: return 2.0
    
    df['bhk'] = df['size'].apply(parse_bhk)
    df['bath'] = df['bath'].fillna(2.0)
    df['balcony'] = df['balcony'].fillna(1.0)
    
    # Drop NaNs in essential cols
    df = df.dropna(subset=['total_sqft_num', 'price', 'location', 'area_type'])
    
    # Simple Outlier filtering to prevent extreme skew
    # 1. Ensure at least 300 sqft per bedroom (standard heuristic)
    df['sqft_per_bhk_temp'] = df['total_sqft_num'] / df['bhk']
    df = df[df['sqft_per_bhk_temp'] >= 300]
    
    df['price_per_sqft'] = df['price'] * 100000 / df['total_sqft_num']
    # Keep between 5th and 90th percentile to prevent heavy tail destruction of OLS
    q_low = df['price_per_sqft'].quantile(0.05)
    q_high = df['price_per_sqft'].quantile(0.90)
    df = df[(df['price_per_sqft'] >= q_low) & (df['price_per_sqft'] <= q_high)]
    
    # 2. Extract X and y
    y = df['price'].values  # Predict price directly for Newton-Raphson
    
    # FEATURE ENGINEERING
    df['sqft_per_bhk'] = df['total_sqft_num'] / df['bhk']
    df['bath_per_bhk'] = df['bath'] / df['bhk']
    
    # 3. Categorical encoding
    # Group rare locations
    loc_counts = df['location'].value_counts()
    rare_locs = loc_counts[loc_counts <= 10].index
    df['location_clean'] = df['location'].apply(lambda x: 'Other' if x in rare_locs else str(x).strip())
    
    # Get dummies for location
    X_loc = pd.get_dummies(df['location_clean'], prefix='loc', drop_first=True)
    
    # Clean area_type and get dummies
    df['area_clean'] = df['area_type'].apply(lambda x: str(x).strip())
    X_area = pd.get_dummies(df['area_clean'], prefix='area', drop_first=False)
    
    # Base numeric features
    X_num = df[['total_sqft_num', 'bhk', 'bath', 'balcony', 'sqft_per_bhk', 'bath_per_bhk']]
    
    X_df = pd.concat([X_num, X_area, X_loc], axis=1).fillna(0)
    columns = X_df.columns.tolist()
    
    X_raw = X_df.values.astype(np.float64)
    
    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(X_raw, y, test_size=0.2, random_state=42)
    
    # 4. Standard Scaling (Only scale numeric columns to prevent sparse categorical explosion)
    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(X_train[:, :6])
    X_test_num = scaler.transform(X_test[:, :6])
    
    X_train_scaled = np.c_[X_train_num, X_train[:, 6:]]
    X_test_scaled = np.c_[X_test_num, X_test[:, 6:]]
    
    # 5. Add Bias column (Intercept)
    X_train_final = np.c_[np.ones(X_train_scaled.shape[0]), X_train_scaled]
    X_test_final = np.c_[np.ones(X_test_scaled.shape[0]), X_test_scaled]
    
    return X_train_final, X_test_final, y_train, y_test, columns, scaler
