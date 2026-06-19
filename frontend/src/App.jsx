import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [locations, setLocations] = useState([]);
  const [areaTypes, setAreaTypes] = useState([]);
  const [formData, setFormData] = useState({
    location: '',
    area_type: '',
    sqft: 1200,
    bhk: 2,
    bath: 2
  });
  const [price, setPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch metadata from backend on mount
  useEffect(() => {
    fetch('http://localhost:5000/metadata')
      .then(res => res.json())
      .then(data => {
        if (data.locations) {
          const sortedLocs = data.locations.sort();
          setLocations(sortedLocs);
          const sortedAreas = data.area_types ? data.area_types.sort() : [];
          setAreaTypes(sortedAreas);
          
          setFormData(prev => ({ 
            ...prev, 
            location: sortedLocs.length > 0 ? sortedLocs[0] : '',
            area_type: sortedAreas.length > 0 ? sortedAreas[0] : ''
          }));
        }
      })
      .catch(err => {
        console.error("Failed to fetch metadata:", err);
      });
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPrice(null);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Prediction failed. Ensure Flask backend is running.');
      }

      const data = await response.json();
      setPrice(data.price_lakhs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container glass-panel">
      <div className="header">
        <h1>Bengaluru Real Estate</h1>
        <p>AI-Powered House Price Predictor</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Location</label>
          <select 
            className="input-field" 
            name="location" 
            value={formData.location}
            onChange={handleInputChange}
            required
          >
            {locations.length === 0 && <option value="">Start Flask backend to load data...</option>}
            {locations.map(loc => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Area Type</label>
          <select 
            className="input-field" 
            name="area_type" 
            value={formData.area_type}
            onChange={handleInputChange}
            required
          >
            {areaTypes.length === 0 && <option value="">Loading area types...</option>}
            {areaTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Total Square Feet</label>
          <input 
            type="number" 
            step="any"
            className="input-field" 
            name="sqft" 
            value={formData.sqft}
            onChange={handleInputChange}
            min="100"
            max="20000"
            required
          />
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>BHK</label>
            <input 
              type="number" 
              className="input-field" 
              name="bhk" 
              value={formData.bhk}
              onChange={handleInputChange}
              min="1"
              max="10"
              required
            />
          </div>

          <div className="form-group" style={{ flex: 1 }}>
            <label>Bathrooms</label>
            <input 
              type="number" 
              className="input-field" 
              name="bath" 
              value={formData.bath}
              onChange={handleInputChange}
              min="1"
              max="10"
              required
            />
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Predict Price'}
        </button>
      </form>

      {error && <div className="error-msg">{error}</div>}

      {price !== null && (
        <div className="result-card">
          <h3>Estimated Value</h3>
          <div className="price">₹ {price.toFixed(2)} Lakhs</div>
        </div>
      )}
    </div>
  )
}

export default App
