import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMealPlans, generateMealPlan } from '../services/api';
import type { MealPlan } from '../types';

export default function MealPlansPage() {
  const [plans, setPlans] = useState<MealPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [weekStart, setWeekStart] = useState(() => {
    // Default to next Monday
    const now = new Date();
    const day = now.getDay();
    const diff = day === 0 ? 1 : 8 - day;
    const nextMon = new Date(now);
    nextMon.setDate(now.getDate() + diff);
    return nextMon.toISOString().split('T')[0];
  });
  const [mealTypes, setMealTypes] = useState<string[]>(['breakfast', 'lunch', 'dinner']);
  const [cookingSessions, setCookingSessions] = useState<string>('');
  const [weeklyBudget, setWeeklyBudget] = useState<string>('');
  const [batchCooking, setBatchCooking] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    getMealPlans()
      .then((res) => setPlans(res.data.sort((a, b) => b.week_start.localeCompare(a.week_start))))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const res = await generateMealPlan({
        week_start: weekStart,
        meal_types: mealTypes,
        cooking_sessions: cookingSessions ? parseInt(cookingSessions) : null,
        weekly_budget: weeklyBudget ? parseFloat(weeklyBudget) : null,
        batch_cooking: batchCooking,
      });
      navigate(`/meal-plans/${res.data.id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to generate meal plan';
      setError(msg);
    } finally {
      setGenerating(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading meal plans...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Meal Plans</h1>

      {/* Generate new plan */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Generate New Meal Plan</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Week Starting</label>
            <input
              type="date"
              value={weekStart}
              onChange={(e) => setWeekStart(e.target.value)}
              className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Meal Types</label>
            <div className="flex gap-4 mt-1">
              {['breakfast', 'lunch', 'dinner'].map((type) => (
                <label key={type} className="flex items-center gap-1.5 text-sm text-gray-700">
                  <input
                    type="checkbox"
                    checked={mealTypes.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setMealTypes([...mealTypes, type]);
                      } else {
                        setMealTypes(mealTypes.filter((t) => t !== type));
                      }
                    }}
                    className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Cooking Sessions</label>
            <input
              type="number"
              min="1"
              value={cookingSessions}
              onChange={(e) => setCookingSessions(e.target.value)}
              placeholder="Leave blank for no limit"
              className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Weekly Budget ($)</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={weeklyBudget}
              onChange={(e) => setWeeklyBudget(e.target.value)}
              placeholder="Optional"
              className="border rounded-lg px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 mb-4">
          <input
            type="checkbox"
            id="batchCooking"
            checked={batchCooking}
            onChange={(e) => setBatchCooking(e.target.checked)}
            className="rounded border-gray-300 text-green-600 focus:ring-green-500"
          />
          <label htmlFor="batchCooking" className="text-sm text-gray-700">
            Plan leftovers to reduce cooking sessions
          </label>
        </div>

        <button
          onClick={handleGenerate}
          disabled={generating || !weekStart}
          className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {generating ? 'Generating...' : 'Generate Meal Plan'}
        </button>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      {/* Past meal plans */}
      <div className="bg-white rounded-lg shadow">
        <h2 className="text-lg font-semibold text-gray-700 px-6 pt-6 pb-2">Past Meal Plans</h2>
        {plans.length === 0 ? (
          <p className="px-6 pb-6 text-gray-500 text-sm">
            No meal plans yet. Generate your first one above!
          </p>
        ) : (
          <ul className="divide-y divide-gray-100">
            {plans.map((plan) => (
              <li key={plan.id}>
                <button
                  onClick={() => navigate(`/meal-plans/${plan.id}`)}
                  className="w-full text-left px-6 py-4 hover:bg-green-50 transition-colors flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium text-gray-800">
                      Week of {formatDate(plan.week_start)}
                    </p>
                    <p className="text-sm text-gray-500">{plan.days.length} days planned</p>
                  </div>
                  <span className="text-green-600 text-sm font-medium">View &rarr;</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
