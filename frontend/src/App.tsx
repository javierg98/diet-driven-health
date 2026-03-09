import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';

function App() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    getMe()
      .then(() => setLoggedIn(true))
      .catch(() => setLoggedIn(false));
  }, []);

  if (loggedIn === null) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={loggedIn ? <div>Dashboard (coming soon)</div> : <Navigate to="/login" />} />
          <Route path="/login" element={<div>Login (coming soon)</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
