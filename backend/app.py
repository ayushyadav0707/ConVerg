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
    # No columns dropped, using all 9!
    df = df.dropna(subset=['price'])
    
    # Fill balcony NaNs with 0
    if 'balcony' in df.columns:
        df['balcony'] = df['balcony'].fillna(0).astype(float)
        
    # Fill society NaNs with Private Property
    if 'society' in df.columns:
        df['society'] = df['society'].fillna('Private Property')
        df['society'] = df['society'].apply(lambda x: str(x).strip())
        society_stats = df['society'].value_counts(ascending=False)
        society_stats_less_than_10 = society_stats[society_stats <= 10]
        df['society'] = df['society'].apply(lambda x: 'other' if x in society_stats_less_than_10 else x)
        
    if 'availability' in df.columns:
        df['availability'] = df['availability'].fillna('Ready To Move')
        df['availability'] = df['availability'].apply(lambda x: 'Ready To Move' if 'Ready' in str(x) or 'Immediate' in str(x) else 'Under Construction')
    
    if 'size' in df.columns:
        df['bhk'] = df['size'].apply(lambda x: int(x.split(' ')[0]) if isinstance(x, str) else x)
        df = df.drop('size', axis=1)
        
    if 'total_sqft' in df.columns:
        df['total_sqft'] = df['total_sqft'].apply(convert_sqft_to_num)
        df = df.dropna(subset=['total_sqft'])
        
    if 'total_sqft' in df.columns and 'bhk' in df.columns:
        df = df[~(df.total_sqft / df.bhk < 300)]
        
    if 'location' in df.columns:
        df['location'] = df['location'].fillna('other')
        df['location'] = df['location'].apply(lambda x: str(x).strip())
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
    
    # Ensure remaining NaNs are dropped for stability
    df = df.dropna()
    return df

def prepare_features(df):
    # One Hot Encode Categorical Variables
    if 'location' in df.columns:
        dummies = pd.get_dummies(df['location'], prefix='loc')
        if 'loc_other' in dummies.columns:
            dummies = dummies.drop('loc_other', axis=1)
        df = pd.concat([df.drop('location', axis=1), dummies], axis=1)
        
    if 'area_type' in df.columns:
        dummies_area = pd.get_dummies(df['area_type'], prefix='area')
        df = pd.concat([df.drop('area_type', axis=1), dummies_area], axis=1)
        
    if 'society' in df.columns:
        dummies_soc = pd.get_dummies(df['society'], prefix='soc')
        if 'soc_other' in dummies_soc.columns:
            dummies_soc = dummies_soc.drop('soc_other', axis=1)
        df = pd.concat([df.drop('society', axis=1), dummies_soc], axis=1)
        
    if 'availability' in df.columns:
        dummies_avail = pd.get_dummies(df['availability'], prefix='avail')
        df = pd.concat([df.drop('availability', axis=1), dummies_avail], axis=1)
        
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
        # Increase regularization if heavily multicollinear
        H = 2 * XT_X + (lambda_reg * 100) * np.eye(D)
        H_inv = np.linalg.inv(H)
        
    y_pred = np.dot(X_with_bias, theta)
    G = -2 * np.dot(X_with_bias.T, (y - y_pred))
    theta = theta - np.dot(H_inv, G)
    return theta

def train_model():
    global theta_global, columns_global
    dataset_path = 'data/bengaluru_house_prices_cleaned.csv'
    if not os.path.exists(dataset_path):
        dataset_path = 'backend/data/bengaluru_house_prices_cleaned.csv'
        
    if not os.path.exists(dataset_path):
        dataset_path = '../backend/data/bengaluru_house_prices_cleaned.csv'
        
    if not os.path.exists(dataset_path):
        print("Dataset not found!")
        return False
        
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    df_cleaned = clean_data(df)
    X_df, y = prepare_features(df_cleaned)
    columns_global = X_df.columns
    X_mat = X_df.values.astype(float)
    
    print(f"Training on matrix shape: {X_mat.shape} with {X_df.shape[1]} features.")
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
    society = data.get('society', '')
    availability = data.get('availability', '')
    
    sqft = float(data.get('sqft', 0))
    bath = int(data.get('bath', 0))
    bhk = int(data.get('bhk', 0))
    balcony = float(data.get('balcony', 0))
    
    x = np.zeros(len(columns_global))
    
    # Continuous variables
    if 'total_sqft' in columns_global:
        x[np.where(columns_global == 'total_sqft')[0][0]] = sqft
    if 'bath' in columns_global:
        x[np.where(columns_global == 'bath')[0][0]] = bath
    if 'bhk' in columns_global:
        x[np.where(columns_global == 'bhk')[0][0]] = bhk
    if 'balcony' in columns_global:
        x[np.where(columns_global == 'balcony')[0][0]] = balcony
        
    # Categorical variables
    loc_col = f"loc_{location}"
    if loc_col in columns_global:
        x[np.where(columns_global == loc_col)[0][0]] = 1
    elif 'loc_other' in columns_global:
        x[np.where(columns_global == 'loc_other')[0][0]] = 1
        
    area_col = f"area_{area_type}"
    if area_col in columns_global:
        x[np.where(columns_global == area_col)[0][0]] = 1
        
    soc_col = f"soc_{society}"
    if soc_col in columns_global:
        x[np.where(columns_global == soc_col)[0][0]] = 1
    elif 'soc_other' in columns_global:
        x[np.where(columns_global == 'soc_other')[0][0]] = 1
        
    avail_col = f"avail_{availability}"
    if avail_col in columns_global:
        x[np.where(columns_global == avail_col)[0][0]] = 1
        
    x_with_bias = np.insert(x, 0, 1)
    price = np.dot(x_with_bias, theta_global)
    
    # --- Mathematical Proof for Evaluators ---
    breakdown = []
    breakdown.append({
        "feature": "Base Parameter (Bias)", 
        "value": 1, 
        "weight": float(theta_global[0]), 
        "contribution": float(theta_global[0])
    })
    
    def add_breakdown(feature_name, display_name, val):
        if feature_name in columns_global:
            idx = np.where(columns_global == feature_name)[0][0] + 1
            w = float(theta_global[idx])
            breakdown.append({"feature": display_name, "value": val, "weight": w, "contribution": val * w})
            
    add_breakdown('total_sqft', "Total Sqft", sqft)
    add_breakdown('bath', "Bathrooms", bath)
    add_breakdown('bhk', "BHK", bhk)
    add_breakdown('balcony', "Balcony", balcony)
    
    if area_col in columns_global:
        add_breakdown(area_col, f"Area ({area_type})", 1)
        
    loc_used = loc_col if loc_col in columns_global else 'loc_other'
    add_breakdown(loc_used, f"Location ({loc_used.replace('loc_', '')})", 1)
    
    soc_used = soc_col if soc_col in columns_global else 'soc_other'
    add_breakdown(soc_used, f"Society ({soc_used.replace('soc_', '')})", 1)
    
    if avail_col in columns_global:
        add_breakdown(avail_col, f"Availability ({availability})", 1)
    
    return jsonify({
        'price_lakhs': float(price),
        'math_proof': {
            'matrix_shape': f"{len(theta_global)}x{len(theta_global)}",
            'breakdown': breakdown
        }
    })

@app.route('/metadata', methods=['GET'])
def get_metadata():
    if columns_global is None:
        return jsonify({'locations': [], 'area_types': [], 'societies': [], 'availabilities': []})
    
    locations = [col.replace('loc_', '') for col in columns_global if col.startswith('loc_')]
    area_types = [col.replace('area_', '') for col in columns_global if col.startswith('area_')]
    societies = [col.replace('soc_', '') for col in columns_global if col.startswith('soc_')]
    availabilities = [col.replace('avail_', '') for col in columns_global if col.startswith('avail_')]
    
    return jsonify({
        'locations': locations, 
        'area_types': area_types,
        'societies': societies,
        'availabilities': availabilities
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
