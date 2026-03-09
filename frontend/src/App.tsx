import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

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
      <Routes>
        <Route path="/login" element={!loggedIn ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/register" element={!loggedIn ? <RegisterPage /> : <Navigate to="/" />} />
        <Route path="/*" element={
          loggedIn ? (
            <Layout>
              <Routes>
                <Route path="/" element={<div>Dashboard (coming next)</div>} />
                <Route path="/meal-plans" element={<div>Meal Plans (coming soon)</div>} />
                <Route path="/recipes" element={<div>Recipes (coming soon)</div>} />
                <Route path="/history" element={<div>History (coming soon)</div>} />
                <Route path="/profile" element={<div>Profile (coming soon)</div>} />
              </Routes>
            </Layout>
          ) : <Navigate to="/login" />
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
