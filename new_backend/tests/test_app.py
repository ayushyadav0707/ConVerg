import sys
import os
import json
import pytest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

from unittest.mock import patch
import numpy as np

import app as app_module

def test_negative_price_clamp_and_breakdown(client):
    payload = {
        "sqft": 500,
        "bhk": 2,
        "bath": 2,
        "balcony": 1,
        "location": "Whitefield",
        "area_type": "Super built-up Area"
    }
    
    # Mock global weights so bias is strongly negative, triggering clamp naturally
    # This prevents breaking the `assert np.isclose(breakdown_sum, pred_price)` invariant
    mock_weights = np.zeros(len(app_module.unscaled_weights))
    mock_weights[0] = -15.0
    
    with patch('app.unscaled_weights', new=mock_weights):
        response = client.post('/predict', json=payload)
        
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['price_lakhs'] == 0.0
    assert data['clamped'] is True
    assert data['raw_prediction'] == -15.0
    
    # Mathematical invariant MUST still hold against raw prediction
    breakdown_sum = sum(item['contribution'] for item in data['breakdown'])
    assert abs(breakdown_sum - data['raw_prediction']) < 1e-4

def test_sqft_100_boundary_valid(client):
    payload = {
        "sqft": 100,
        "bhk": 2,
        "bath": 2,
        "balcony": 1,
        "location": "Whitefield",
        "area_type": "Super built-up Area"
    }
    response = client.post('/predict', json=payload)
    assert response.status_code == 200
    assert 'price_lakhs' in response.get_json()

def test_sqft_99_boundary_invalid(client):
    payload = {
        "sqft": 99,
        "bhk": 2,
        "bath": 2,
        "balcony": 1,
        "location": "Whitefield",
        "area_type": "Super built-up Area"
    }
    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "Square footage must be between 100 and 10000" in data['error']
