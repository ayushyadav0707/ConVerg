import { useState, useEffect } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function App() {
  const [locations, setLocations] = useState([]);
  const [areaTypes, setAreaTypes] = useState([]);
  
  const today = new Date().toISOString().split('T')[0];
  
  const [formData, setFormData] = useState({
    location: '',
    area_type: '',
    availability: today,
    sqft: 1200,
    bhk: 2,
    bath: 2,
    balcony: 1
  });
  const [price, setPrice] = useState(null);
  const [mathProof, setMathProof] = useState(null);
  const [showProof, setShowProof] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Location search state
  const [locationSearch, setLocationSearch] = useState('');
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);

  const filteredLocations = locations.filter(loc => 
    loc.toLowerCase().includes(locationSearch.toLowerCase())
  );

  // Fetch metadata from backend on mount
  useEffect(() => {
    fetch(`${API_URL}/metadata`)
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
    setMathProof(null);

    // Map Calendar Date to ML string
    const selectedDate = new Date(formData.availability);
    const currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);
    const availStatus = selectedDate <= currentDate ? "Ready To Move" : "Under Construction";

    const payload = {
      ...formData,
      availability: availStatus
    };

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Prediction failed. Ensure Flask backend is running.');
      }

      const data = await response.json();
      setPrice(data.price_lakhs);
      setMathProof(data.math_proof);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <div className="dashboard-layout">
        <div className="left-panel glass-panel">
      <div className="header">
        <img src="/logo.png" alt="ConVerg Logo" className="app-logo" />
        <h1>Bengaluru Real Estate</h1>
        <p>AI-Powered House Price Predictor</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label>Location</label>
            <div style={{ position: 'relative' }}>
              <input 
                type="text" 
                className="input-field" 
                placeholder="Search Location..." 
                value={showLocationDropdown ? locationSearch : formData.location}
                onChange={(e) => {
                  setLocationSearch(e.target.value);
                  setShowLocationDropdown(true);
                }}
                onFocus={() => {
                  setLocationSearch('');
                  setShowLocationDropdown(true);
                }}
                onBlur={() => setTimeout(() => setShowLocationDropdown(false), 200)}
                required
              />
              {showLocationDropdown && (
                <ul className="custom-dropdown">
                  {filteredLocations.length > 0 ? (
                    filteredLocations.map(loc => (
                      <li key={loc} onClick={() => {
                        setFormData({ ...formData, location: loc });
                        setLocationSearch('');
                        setShowLocationDropdown(false);
                      }}>
                        {loc}
                      </li>
                    ))
                  ) : (
                    <li style={{ color: '#ef4444' }}>No location found</li>
                  )}
                </ul>
              )}
            </div>
          </div>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label>Area Type</label>
            <select className="input-field" name="area_type" value={formData.area_type} onChange={handleInputChange} required>
              {areaTypes.length === 0 && <option value="">Loading...</option>}
              {areaTypes.map(type => <option key={type} value={type}>{type}</option>)}
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="form-group" style={{ flex: 1, marginBottom: 0 }}>
            <label>Availability Date</label>
            <input type="date" className="input-field" name="availability" value={formData.availability} onChange={handleInputChange} required />
          </div>
        </div>

        <div className="form-group">
          <label>Total Square Feet</label>
          <input type="number" step="any" className="input-field" name="sqft" value={formData.sqft} onChange={handleInputChange} min="100" max="20000" required />
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>BHK</label>
            <input type="number" className="input-field" name="bhk" value={formData.bhk} onChange={handleInputChange} min="1" max="10" required />
          </div>

          <div className="form-group" style={{ flex: 1 }}>
            <label>Bathrooms</label>
            <input type="number" className="input-field" name="bath" value={formData.bath} onChange={handleInputChange} min="1" max="10" required />
          </div>

          <div className="form-group" style={{ flex: 1 }}>
            <label>Balconies</label>
            <input type="number" className="input-field" name="balcony" value={formData.balcony} onChange={handleInputChange} min="0" max="10" required />
          </div>
        </div>

        <button type="submit" className="submit-btn" disabled={loading}>
          {loading ? 'Calculating...' : 'Predict Price'}
        </button>
      </form>

      {error && <div className="error-msg">{error}</div>}
      </div>

      {price !== null && (
        <div className="right-panel glass-panel">
          <div className="result-card">
            <h3>Estimated Value</h3>
            <div className="price">₹ {price.toFixed(2)} Lakhs</div>
            
            {mathProof && (
              <div className="proof-section">
              <button 
                className="proof-toggle-btn" 
                onClick={() => setShowProof(!showProof)}
                type="button"
              >
                {showProof ? 'Hide' : 'Show'} Newton-Raphson Mathematical Proof
              </button>
              
              {showProof && (
                <div className="proof-content">
                  <p className="proof-subtitle">
                    Proof of Work: Evaluated using exact Newton-Raphson Optimization. <br/>
                    Hessian Matrix Shape: <strong>{mathProof.matrix_shape}</strong>
                  </p>

                  <div className="proof-formulas">
                    <h4>Applied Methodology (Multivariate Matrix Calculus)</h4>
                    <ul>
                      <li><strong>Prediction:</strong> <br/><code style={{color: '#ec4899'}}>Y_pred = X · θ</code></li>
                      <li><strong>Gradient (1st Derivative):</strong> <br/><code style={{color: '#10b981'}}>G = -2 Xᵀ(Y - Y_pred)</code></li>
                      <li><strong>Hessian (2nd Derivative):</strong> <br/><code style={{color: '#818cf8'}}>H = 2 Xᵀ X</code></li>
                      <li><strong>Newton-Raphson Update:</strong> <br/><code style={{color: '#f59e0b'}}>θ_new = θ_old - H⁻¹ · G</code></li>
                    </ul>
                  </div>
                  
                  <table className="proof-table">
                    <thead>
                      <tr>
                        <th>Feature Evaluated</th>
                        <th>Value</th>
                        <th>Trained Weight (θ)</th>
                        <th>Contribution</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mathProof.breakdown.map((item, index) => (
                        <tr key={index}>
                          <td>{item.feature}</td>
                          <td>{item.value}</td>
                          <td>{item.weight.toFixed(4)}</td>
                          <td className="highlight">{(item.contribution).toFixed(4)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot>
                      <tr>
                        <td colSpan="3" style={{textAlign: 'right'}}><strong>Final Price Sum:</strong></td>
                        <td className="highlight-sum">{price.toFixed(4)} Lakhs</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
        </div>
      )}
      </div>
    </div>
  )
}

export default App
