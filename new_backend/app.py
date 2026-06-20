import os
import json
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), static_folder=os.path.join(base_dir, 'static'))
CORS(app)

# Load Model
weights_path = os.path.join(base_dir, 'model_weights.json')

with open(weights_path, 'r') as f:
    model_data = json.load(f)

columns = model_data['columns']
theta = np.array(model_data['theta_nr'])
scaler_mean = np.array(model_data['scaler']['mean'])
scaler_scale = np.array(model_data['scaler']['scale'])

# Extract locations for the frontend dropdown
locations = [col.replace('loc_', '') for col in columns if col.startswith('loc_')]
locations.sort()

# Add standard 'Other' location fallback
if 'Other' not in locations:
    locations.append('Other')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predictor')
def predictor():
    return render_template('predictor.html', locations=locations)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        sqft = float(data.get('sqft', 1000))
        bhk = float(data.get('bhk', 2))
        bath = float(data.get('bath', 2))
        balcony = float(data.get('balcony', 1))
        loc = data.get('location', 'Other')
        
        # Build feature vector
        x = np.zeros(len(columns))
        for i, col in enumerate(columns):
            if col == 'total_sqft_num': x[i] = sqft
            elif col == 'bhk': x[i] = bhk
            elif col == 'bath': x[i] = bath
            elif col == 'balcony': x[i] = balcony
            elif col == 'sqft_per_bhk': x[i] = sqft / float(bhk) if bhk > 0 else 0.0
            elif col == 'bath_per_bhk': x[i] = bath / float(bhk) if bhk > 0 else 0.0
            elif col.startswith('loc_'):
                if col == f'loc_{loc}':
                    x[i] = 1.0
                    
        # Extract numeric features and scale them using training moments
        num_features = x[:6]
        scaled_num = (num_features - scaler_mean) / scaler_scale
        
        # Replace the unscaled numeric features with scaled ones
        x_scaled = np.copy(x)
        x_scaled[:6] = scaled_num
        
        # Add bias
        x_final = np.concatenate(([1.0], x_scaled))
        
        # Dot product prediction
        pred_price = np.dot(x_final, theta)
        
        # Ensure no negative prices
        pred_price = max(0.0, float(pred_price))
        
        return jsonify({'price_lakhs': pred_price})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("Starting Newton-Raphson API on Localhost...")
    app.run(host='127.0.0.1', port=5000, debug=False)
