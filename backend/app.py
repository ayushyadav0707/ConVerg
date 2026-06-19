import numpy as np
import pandas as pd
import os
import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS

warnings.filterwarnings("ignore")

app = Flask(__name__)
CORS(app)  # Enable CORS for the React frontend

# Global variables for the trained model
theta_global = None
columns_global = None

def convert_sqft_to_num(x):
    if not isinstance(x, str):
        return x
    tokens = x.split('-')
    if len(tokens) == 2:
        return (float(tokens[0]) + float(tokens[1])) / 2
    try:
        return float(x)
    except:
        return None

def clean_data(df):
    cols_to_drop = ['society', 'balcony', 'availability']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
    df = df.dropna()
    
    if 'size' in df.columns:
        df['bhk'] = df['size'].apply(lambda x: int(x.split(' ')[0]) if isinstance(x, str) else x)
        df = df.drop('size', axis=1)
        
    if 'total_sqft' in df.columns:
        df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_num)
        df = df.dropna(subset=['total_sqft'])
        
    if 'total_sqft' in df.columns and 'bhk' in df.columns:
        df = df[~(df.total_sqft / df.bhk < 300)]
        
    if 'location' in df.columns:
        df['location'] = df['location'].apply(lambda x: x.strip())
        location_stats = df['location'].value_counts(ascending=False)
        location_stats_less_than_10 = location_stats[location_stats <= 10]
        df['location'] = df['location'].apply(lambda x: 'other' if x in location_stats_less_than_10 else x)
        
    def remove_pps_outliers(df):
        df_out = pd.DataFrame()
        if 'price' not in df.columns or 'total_sqft' not in df.columns or 'location' not in df.columns:
            return df
        
        df['price_per_sqft'] = df['price'] * 100000 / df['total_sqft']
        for key, subdf in df.groupby('location'):
            m = np.mean(subdf.price_per_sqft)
            st = np.std(subdf.price_per_sqft)
            reduced_df = subdf[(subdf.price_per_sqft > (m - st)) & (subdf.price_per_sqft <= (m + st))]
            df_out = pd.concat([df_out, reduced_df], ignore_index=True)
        return df_out.drop('price_per_sqft', axis=1, errors='ignore')
        
    df = remove_pps_outliers(df)
    return df

def prepare_features(df):
    if 'location' in df.columns:
        dummies = pd.get_dummies(df['location'], prefix='loc')
        if 'loc_other' in dummies.columns:
            dummies = dummies.drop('loc_other', axis=1)
        df = pd.concat([df.drop('location', axis=1), dummies], axis=1)
        
    if 'area_type' in df.columns:
        dummies_area = pd.get_dummies(df['area_type'], prefix='area')
        df = pd.concat([df.drop('area_type', axis=1), dummies_area], axis=1)
        
    y = df['price'].values
    X_df = df.drop('price', axis=1)
    return X_df, y

def newton_raphson_multivariate(X, y, lambda_reg=0.01):
    X_with_bias = np.c_[np.ones(X.shape[0]), X]
    N, D = X_with_bias.shape
    theta = np.zeros(D)
    XT_X = np.dot(X_with_bias.T, X_with_bias)
    H = 2 * XT_X + lambda_reg * np.eye(D)
    
    try:
        H_inv = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        H = 2 * XT_X + (lambda_reg * 100) * np.eye(D)
        H_inv = np.linalg.inv(H)
        
    y_pred = np.dot(X_with_bias, theta)
    G = -2 * np.dot(X_with_bias.T, (y - y_pred))
    theta = theta - np.dot(H_inv, G)
    return theta

def train_model():
    global theta_global, columns_global
    # Try looking in backend directory or parent directory
    dataset_path = 'bengaluru_house_prices.csv'
    if not os.path.exists(dataset_path):
        dataset_path = '../bengaluru_house_prices.csv'
        
    if not os.path.exists(dataset_path):
        print("Dataset not found!")
        return False
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    df_cleaned = clean_data(df)
    X_df, y = prepare_features(df_cleaned)
    columns_global = X_df.columns
    X_mat = X_df.values.astype(float)
    
    theta_global = newton_raphson_multivariate(X_mat, y)
    print("Model trained successfully.")
    return True

# Train the model when the server starts
train_model()

@app.route('/predict', methods=['POST'])
def predict():
    if theta_global is None or columns_global is None:
        return jsonify({'error': 'Model not trained.'}), 500
        
    data = request.json
    location = data.get('location', '')
    area_type = data.get('area_type', '')
    sqft = float(data.get('sqft', 0))
    bath = int(data.get('bath', 0))
    bhk = int(data.get('bhk', 0))
    
    x = np.zeros(len(columns_global))
    
    if 'total_sqft' in columns_global:
        x[np.where(columns_global == 'total_sqft')[0][0]] = sqft
    if 'bath' in columns_global:
        x[np.where(columns_global == 'bath')[0][0]] = bath
    if 'bhk' in columns_global:
        x[np.where(columns_global == 'bhk')[0][0]] = bhk
        
    loc_col = f"loc_{location}"
    if loc_col in columns_global:
        loc_index = np.where(columns_global == loc_col)[0][0]
        x[loc_index] = 1
    elif 'loc_other' in columns_global:
        loc_index = np.where(columns_global == 'loc_other')[0][0]
        x[loc_index] = 1
        
    area_col = f"area_{area_type}"
    if area_col in columns_global:
        area_index = np.where(columns_global == area_col)[0][0]
        x[area_index] = 1
        
    x_with_bias = np.insert(x, 0, 1)
    price = np.dot(x_with_bias, theta_global)
    
    return jsonify({'price_lakhs': float(price)})

@app.route('/metadata', methods=['GET'])
def get_metadata():
    if columns_global is None:
        return jsonify({'locations': [], 'area_types': []})
    
    locations = [col.replace('loc_', '') for col in columns_global if col.startswith('loc_')]
    area_types = [col.replace('area_', '') for col in columns_global if col.startswith('area_')]
    return jsonify({'locations': locations, 'area_types': area_types})

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=5000)
