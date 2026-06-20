import React from 'react';
import './LandingPage.css';

export default function LandingPage({ onStart }) {
  return (
    <div className="landing-container">
      {/* Navbar */}
      <nav className="converg-nav">
        <div className="nav-brand">
          <img src="/logo.png" alt="ConVerg Logo" className="nav-logo" />
          <span className="brand-name">CONVERG HOUSE</span>
        </div>
        <button className="nav-btn" onClick={onStart}>Get Started &rarr;</button>
      </nav>

      {/* Hero Section */}
      <main className="hero-section">
        <div className="hero-logo-container">
           <img src="/logo.png" alt="ConVerg Logo Main" className="hero-logo-large" />
        </div>
        
        <h1 className="hero-headline">
          Predict House Prices <br/>
          Using <span className="gradient-text">Engineering Mathematics</span>
        </h1>
        
        <p className="hero-subtitle">
          Converg House combines engineering mathematics,<br/>
          statistical modeling, and machine learning to estimate<br/>
          property values using real-world housing data.
        </p>

        {/* Stats Row */}
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-icon stat-blue">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            </div>
            <div className="stat-text">
              <h4>Highly</h4>
              <span>Accurate</span>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon stat-green">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            </div>
            <div className="stat-text">
              <h4>13,000+</h4>
              <span>Housing Records</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-yellow">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
            </div>
            <div className="stat-text">
              <h4>Real-Time</h4>
              <span>Predictions</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-purple">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            </div>
            <div className="stat-text">
              <h4>Location</h4>
              <span>Intelligence</span>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon stat-indigo">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            </div>
            <div className="stat-text">
              <h4>Mathematical</h4>
              <span>Modeling</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="hero-actions">
          <button className="btn-primary" onClick={onStart}>Predict Now &rarr;</button>
        </div>
      </main>

      {/* Decorative Footer Graphics */}
      <div className="footer-graphics">
        {/* We use CSS background for the wavy line. */}
      </div>

      <div className="footer-tagline">
        DATA. MATHEMATICS. DECISIONS.
      </div>
    </div>
  );
}
