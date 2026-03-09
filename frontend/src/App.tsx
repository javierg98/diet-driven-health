import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import RecipesPage from './pages/RecipesPage';
import RecipeDetailPage from './pages/RecipeDetailPage';
import MealPlansPage from './pages/MealPlansPage';
import MealPlanDetailPage from './pages/MealPlanDetailPage';

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
                <Route path="/" element={<DashboardPage />} />
                <Route path="/meal-plans" element={<MealPlansPage />} />
                <Route path="/meal-plans/:id" element={<MealPlanDetailPage />} />
                <Route path="/recipes" element={<RecipesPage />} />
                <Route path="/recipes/:id" element={<RecipeDetailPage />} />
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
