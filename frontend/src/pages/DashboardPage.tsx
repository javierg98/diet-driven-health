import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMealPlans, getDishLogs, getFavorites, getRecipes } from '../services/api';
import type { MealPlan, DishLog, Recipe } from '../types';

export default function DashboardPage() {
  const [latestPlan, setLatestPlan] = useState<MealPlan | null>(null);
  const [dishLogs, setDishLogs] = useState<DishLog[]>([]);
  const [favCount, setFavCount] = useState(0);
  const [recipes, setRecipes] = useState<Record<number, Recipe>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getMealPlans(),
      getDishLogs(),
      getFavorites(),
      getRecipes(),
    ]).then(([plans, logs, favs, allRecipes]) => {
      if (plans.data.length > 0) {
        setLatestPlan(plans.data[0]);
      }
      setDishLogs(logs.data);
      setFavCount(favs.data.length);
      const recipeMap: Record<number, Recipe> = {};
      allRecipes.data.forEach((r) => { recipeMap[r.id] = r; });
      setRecipes(recipeMap);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading dashboard...</div>;
  }

  const avgRating = dishLogs.length > 0
    ? (dishLogs.reduce((sum, d) => sum + d.rating, 0) / dishLogs.length).toFixed(1)
    : '\u2014';

  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Dashboard</h1>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-3xl font-bold text-green-600">{dishLogs.length}</div>
          <div className="text-sm text-gray-500">Dishes Logged</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-3xl font-bold text-green-600">{avgRating}</div>
          <div className="text-sm text-gray-500">Avg Rating</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 text-center">
          <div className="text-3xl font-bold text-green-600">{favCount}</div>
          <div className="text-sm text-gray-500">Favorites</div>
        </div>
      </div>

      {/* Meal Plan Overview */}
      <h2 className="text-lg font-semibold text-gray-700 mb-3">Current Meal Plan</h2>
      {latestPlan ? (
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-green-50">
                <th className="px-3 py-2 text-left text-green-700">Day</th>
                <th className="px-3 py-2 text-left text-green-700">Breakfast</th>
                <th className="px-3 py-2 text-left text-green-700">Lunch</th>
                <th className="px-3 py-2 text-left text-green-700">Dinner</th>
              </tr>
            </thead>
            <tbody>
              {latestPlan.days.map((day, i) => (
                <tr key={i} className="border-t">
                  <td className="px-3 py-2 font-medium">{dayNames[i]}</td>
                  <td className="px-3 py-2">{day.breakfast !== null ? (recipes[day.breakfast]?.name || `Recipe #${day.breakfast}`) : '—'}</td>
                  <td className="px-3 py-2">{day.lunch !== null ? (recipes[day.lunch]?.name || `Recipe #${day.lunch}`) : '—'}</td>
                  <td className="px-3 py-2">{day.dinner !== null ? (recipes[day.dinner]?.name || `Recipe #${day.dinner}`) : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-3 border-t">
            <Link to="/meal-plans" className="text-green-600 hover:underline text-sm">
              View full meal plan &rarr;
            </Link>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500 mb-4">No meal plan yet. Generate your first one!</p>
          <Link to="/meal-plans" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Create Meal Plan
          </Link>
        </div>
      )}
    </div>
  );
}
