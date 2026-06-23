import os
import json
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), static_folder=os.path.join(base_dir, 'static'))
app.config['TEMPLATES_AUTO_RELOAD'] = True
# Enable CORS for cross-origin frontend requests
CORS(app)

# Load Model
weights_path = os.path.join(base_dir, 'model_weights.json')

with open(weights_path, 'r') as f:
    model_data = json.load(f)

columns = model_data['columns']
theta = np.array(model_data['theta_nr'])
scaler_mean = np.array(model_data['scaler']['mean'])
scaler_scale = np.array(model_data['scaler']['scale'])

# Unscale weights once on startup
num_count = len(scaler_mean)
unscaled_weights = np.copy(theta)
unscaled_weights[1:num_count+1] = theta[1:num_count+1] / scaler_scale
unscaled_weights[0] = theta[0] - np.sum(theta[1:num_count+1] * scaler_mean / scaler_scale)

# Extract locations for the frontend dropdown
locations = [col.replace('loc_', '') for col in columns if col.startswith('loc_')]
locations.sort()

# Extract area types
area_types = [col.replace('area_', '') for col in columns if col.startswith('area_')]
area_types.sort()

# Add standard 'Other' location fallback
if 'Other' not in locations:
    locations.append('Other')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/predictor')
def predictor():
    return render_template('predictor.html', locations=locations, area_types=area_types)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests using the pre-loaded Newton-Raphson model."""
    try:
        data = request.json
        sqft = float(data.get('sqft', 1000))
        bhk = float(data.get('bhk', 2))
        bath = float(data.get('bath', 2))
        
        if not (100 <= sqft <= 10000): return jsonify({'error': 'Square footage must be between 100 and 10000.'}), 400
        if not (1 <= bhk <= 10): return jsonify({'error': 'BHK must be between 1 and 10.'}), 400
        if not (1 <= bath <= 8): return jsonify({'error': 'Bathrooms must be between 1 and 8.'}), 400
        
        balcony = float(data.get('balcony', 1))
        loc = data.get('location', 'Other')
        if not loc or str(loc).strip() == '' or f'loc_{loc}' not in columns:
            loc = 'Other'
        area = data.get('area_type', 'Super built-up  Area')
        
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
            elif col.startswith('area_'):
                if col == f'area_{area}':
                    x[i] = 1.0
        # Add bias
        x_final = np.concatenate(([1.0], x))
        
        # Dot product prediction
        pred_price = np.dot(x_final, unscaled_weights)
        
        # Build calculation breakdown
        breakdown = []
        breakdown_sum = 0.0
        
        bias_contrib = float(unscaled_weights[0])
        breakdown.append({
            "feature": "Bias (Intercept)",
            "value": 1.0,
            "weight": bias_contrib,
            "contribution": bias_contrib
        })
        breakdown_sum += bias_contrib
        
        for i, val in enumerate(x):
            if abs(val) > 1e-4:
                feat_name = columns[i]
                weight = float(unscaled_weights[i+1])
                contrib = float(val * weight)
                breakdown.append({
                    "feature": feat_name,
                    "value": float(val),
                    "weight": weight,
                    "contribution": contrib
                })
                breakdown_sum += contrib
                
        # Ensure mathematical invariant holds against the raw prediction
        assert np.isclose(breakdown_sum, pred_price, rtol=1e-4), "Breakdown doesn't sum to total"
        
        # Clamp negative prices but keep track for UX
        raw_prediction = float(pred_price)
        clamped = False
        if pred_price < 0.0:
            pred_price = 0.0
            clamped = True
        
        theoretical_formulas = (
            "$\\textbf{1. Prediction Equation:} \\\\[1ex] y_{predicted} = wx + b$\n\n"
            "$\\textbf{2. Error Function:} \\\\[1ex] Error = \\sum(y_{actual} - y_{predicted})^2$\n\n"
            "$\\textbf{3. Newton-Raphson Optimization:} \\\\[1ex] w_{new} = w_{old} - \\frac{Gradient}{Hessian}$"
        )
        
        return jsonify({
            'price_lakhs': float(pred_price),
            'raw_prediction': raw_prediction,
            'clamped': clamped,
            'breakdown': breakdown,
            'formula': theoretical_formulas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    print("Starting Newton-Raphson API on Localhost...")
    app.run(host='127.0.0.1', port=5000, debug=False)
