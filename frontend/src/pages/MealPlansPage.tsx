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
      const res = await generateMealPlan({ week_start: weekStart });
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
        <div className="flex flex-col sm:flex-row items-start sm:items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Week Starting</label>
            <input
              type="date"
              value={weekStart}
              onChange={(e) => setWeekStart(e.target.value)}
              className="border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating || !weekStart}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {generating ? 'Generating...' : 'Generate Meal Plan'}
          </button>
        </div>
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
