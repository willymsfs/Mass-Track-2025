import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './Auth';
import Dashboard from './Dashboard';
import MassEntry from './MassEntry';
import ExcelImport from './ExcelImport';
import './App.css';

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  if (!token) {
    return <Auth setToken={setToken} />;
  }

  return (
    <Router>
      <div className="App">
        <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
          <a href="/" style={{ marginRight: '20px' }}>Dashboard</a>
          <a href="/mass-entry" style={{ marginRight: '20px' }}>Record Mass</a>
          <a href="/excel-import">Import Excel</a>
        </nav>
        
        <div style={{ padding: '20px' }}>
          <Routes>
            <Route path="/" element={<Dashboard token={token} setToken={setToken} />} />
            <Route path="/mass-entry" element={<MassEntry token={token} />} />
            <Route path="/excel-import" element={<ExcelImport token={token} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
