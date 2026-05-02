// © 2026 Dre's Autonomous Neural Interface | Whop Nexus Engine
// frontend/src/App.tsx

import React, { useState } from 'react';
import './App.css';

interface Product {
  id: string;
  name: string;
  price: string;
  description: string;
}

const WhopNexus: React.FC = () => {
  const [licenseKey, setLicenseKey] = useState<string>('');
  const [status, setStatus] = useState<string>('Standby');

  const products: Product[] = [
    { id: '1', name: 'Neural Swarm Engine', price: '$99', description: 'Industrial scale agent orchestration.' },
    { id: '2', name: 'PersonaMimic Core', price: '$49', description: 'High-fidelity persona synthesis.' },
  ];

  const validateLicense = async (): Promise<void> => {
    setStatus('Validating...');
    try {
      const response = await fetch(`http://localhost:8000/api/whop/validate-license?license_key=${licenseKey}`);
      const data = await response.json();
      if (data.valid) {
        setStatus('Authorized: ' + data.product);
      } else {
        setStatus('Invalid License');
      }
    } catch (error) {
      setStatus('Connection Error');
    }
  };

  return (
    <div className="nexus-container">
      <header className="nexus-header">
        <h1>Whop Nexus Engine</h1>
        <p className="subtitle">Industrial Digital Asset Management</p>
      </header>

      <main className="nexus-grid">
        <section className="product-list">
          <h2>Marketplace</h2>
          <div className="product-cards">
            {products.map(p => (
              <div key={p.id} className="card">
                <h3>{p.name}</h3>
                <p>{p.description}</p>
                <button className="buy-btn">Buy on Whop ({p.price})</button>
              </div>
            ))}
          </div>
        </section>

        <section className="access-control">
          <h2>Access Gateway</h2>
          <div className="auth-box">
            <input 
              type="text" 
              placeholder="Enter Whop License Key" 
              value={licenseKey}
              onChange={(e) => setLicenseKey(e.target.value)}
            />
            <button onClick={validateLicense}>Unlock Assets</button>
            <div className={`status-indicator ${status.toLowerCase()}`}>
              Status: {status}
            </div>
          </div>
        </section>
      </main>

      <footer className="nexus-footer">
        <p>© 2026 Dre's Autonomous Neural Interface | Secure Industrial Loop</p>
      </footer>
    </div>
  );
};

export default WhopNexus;
