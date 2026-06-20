import { useState, useEffect } from 'react'
import './App.css'
import LandingPage from './LandingPage'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

function App() {
  const [showDashboard, setShowDashboard] = useState(false);
  const [locations, setLocations] = useState([]);
  const [areaTypes, setAreaTypes] = useState([]);
  
  const [formData, setFormData] = useState({
    location: '',
    area_type: '',
    sqft: 1200,
    bhk: 2,
    bath: 2,
    balcony: 1
  });
  const [priceNR, setPriceNR] = useState(null);
  const [priceGD, setPriceGD] = useState(null);
  const [epochsNR, setEpochsNR] = useState(null);
  const [epochsGD, setEpochsGD] = useState(null);
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

  // Fetch metadata from backend on mount with retry logic
  useEffect(() => {
    let isMounted = true;
    let retryCount = 0;
    const maxRetries = 15;
    
    const fetchMetadata = () => {
      fetch(`${API_URL}/metadata`)
        .then(res => {
          if (!res.ok) throw new Error("Backend responded with an error");
          return res.json();
        })
        .then(data => {
          if (!isMounted) return;
          if (data.locations && data.locations.length > 0) {
            const sortedLocs = data.locations.sort();
            setLocations(sortedLocs);
            const sortedAreas = data.area_types ? data.area_types.sort() : [];
            setAreaTypes(sortedAreas);
            
            setFormData(prev => ({ 
              ...prev, 
              location: sortedLocs.length > 0 ? sortedLocs[0] : '',
              area_type: sortedAreas.length > 0 ? sortedAreas[0] : ''
            }));
            setError(''); // Clear errors
          } else {
             if (retryCount < maxRetries) {
               retryCount++;
               setTimeout(fetchMetadata, 2000);
             }
          }
        })
        .catch(err => {
          if (!isMounted) return;
          console.error("Failed to fetch metadata:", err);
          if (retryCount < maxRetries) {
            retryCount++;
            setError(`Backend starting up... (${retryCount}/${maxRetries})`);
            setTimeout(fetchMetadata, 2000);
          } else {
            setError("Failed to connect to backend. Please ensure the Flask server is running on port 5000.");
            setAreaTypes([]);
          }
        });
    };

    fetchMetadata();
    
    return () => { isMounted = false; };
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setPriceNR(null);
    setPriceGD(null);
    setMathProof(null);

    const payload = {
      ...formData,
      availability: "Ready To Move"
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
      setPriceNR(data.price_lakhs_nr);
      setPriceGD(data.price_lakhs_gd);
      setEpochsNR(data.epochs_nr);
      setEpochsGD(data.epochs_gd);
      setMathProof(data.math_proof);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!showDashboard) {
    return <LandingPage onStart={() => setShowDashboard(true)} />;
  }

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
              {areaTypes.length === 0 && <option value="">{error ? 'Waiting for Server...' : 'Loading...'}</option>}
              {areaTypes.map(type => <option key={type} value={type}>{type}</option>)}
            </select>
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

      <div className="right-panel glass-panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: priceNR === null ? 'center' : 'flex-start' }}>
      {priceNR === null ? (
        <div style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: '2rem' }}>
          <svg style={{ width: '64px', height: '64px', opacity: 0.5, marginBottom: '1rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <h2>Ready to Predict</h2>
          <p>Fill out the property details on the left and click Predict Price to see the AI evaluation and mathematical proof.</p>
        </div>
      ) : (
        <div className="result-card" style={{ margin: 0 }}>
          <h3>Estimated Value Comparison</h3>
          
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ flex: 1, padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid rgba(129, 140, 248, 0.3)' }}>
              <h4 style={{ color: '#818cf8', marginBottom: '0.5rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Newton-Raphson</h4>
              <div className="price" style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>₹ {priceNR.toFixed(2)} L</div>
              <div style={{ fontSize: '0.8rem', color: '#aaa' }}>Converged in {epochsNR} epoch(s)</div>
            </div>
            
            <div style={{ flex: 1, padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              <h4 style={{ color: '#10b981', marginBottom: '0.5rem', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>Gradient Descent</h4>
              <div className="price" style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>₹ {priceGD.toFixed(2)} L</div>
              <div style={{ fontSize: '0.8rem', color: '#aaa' }}>Converged in {epochsGD} epoch(s)</div>
            </div>
          </div>
          
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
                        <td colSpan="3" style={{textAlign: 'right'}}><strong>Final Price Sum (NR):</strong></td>
                        <td className="highlight-sum">{priceNR.toFixed(4)} Lakhs</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      )}
      

      
        </div>
      </div>
    </div>
  )
}

export default App
