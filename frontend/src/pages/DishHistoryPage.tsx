import { useState, useEffect, useMemo } from 'react';
import { getDishLogs, getFavorites, getRecipes } from '../services/api';
import type { DishLog, Recipe } from '../types';
import DishLogForm from '../components/DishLogForm';

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="inline-flex gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <span key={star} className={star <= rating ? 'text-yellow-400' : 'text-gray-300'}>
          &#9733;
        </span>
      ))}
    </span>
  );
}

export default function DishHistoryPage() {
  const [tab, setTab] = useState<'all' | 'favorites'>('all');
  const [logs, setLogs] = useState<DishLog[]>([]);
  const [favorites, setFavorites] = useState<DishLog[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  const recipeMap = useMemo(() => {
    const map = new Map<number, string>();
    recipes.forEach((r) => map.set(r.id, r.name));
    return map;
  }, [recipes]);

  const fetchData = () => {
    setLoading(true);
    Promise.all([getDishLogs(), getFavorites(), getRecipes()])
      .then(([logsRes, favsRes, recipesRes]) => {
        setLogs(logsRes.data);
        setFavorites(favsRes.data);
        setRecipes(recipesRes.data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLogged = () => {
    setShowForm(false);
    fetchData();
  };

  const sortedLogs = useMemo(
    () => [...logs].sort((a, b) => new Date(b.date_cooked).getTime() - new Date(a.date_cooked).getTime()),
    [logs],
  );

  const sortedFavorites = useMemo(
    () => [...favorites].sort((a, b) => new Date(b.date_cooked).getTime() - new Date(a.date_cooked).getTime()),
    [favorites],
  );

  const displayLogs = tab === 'all' ? sortedLogs : sortedFavorites;

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading dish history...</div>;
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Dish History</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors"
        >
          {showForm ? 'Cancel' : 'Log a Dish'}
        </button>
      </div>

      {showForm && <DishLogForm recipes={recipes} onLogged={handleLogged} />}

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setTab('all')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            tab === 'all'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          All History
        </button>
        <button
          onClick={() => setTab('favorites')}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            tab === 'favorites'
              ? 'bg-green-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          Favorites
        </button>
      </div>

      {/* Dish log entries */}
      {displayLogs.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          {tab === 'all'
            ? 'No dishes logged yet. Start by logging your first dish!'
            : 'No favorites yet. Rate a dish 4+ stars and mark "would make again" to see it here.'}
        </div>
      ) : (
        <div className="space-y-3">
          {displayLogs.map((log) => (
            <div key={log.id} className="bg-white rounded-lg shadow p-4">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-800 truncate">
                    {recipeMap.get(log.recipe_id) || `Recipe #${log.recipe_id}`}
                  </h3>
                  <div className="flex items-center gap-3 mt-1 text-sm">
                    <StarRating rating={log.rating} />
                    <span className="text-gray-500">
                      {new Date(log.date_cooked).toLocaleDateString()}
                    </span>
                    {log.would_make_again && (
                      <span className="inline-flex items-center bg-green-100 text-green-700 text-xs font-medium px-2 py-0.5 rounded-full">
                        Would make again
                      </span>
                    )}
                  </div>
                </div>
              </div>
              {log.notes && (
                <p className="mt-2 text-sm text-gray-600 line-clamp-2">{log.notes}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
