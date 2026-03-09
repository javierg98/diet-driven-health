import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMealPlan, getRecipes, swapMeal } from '../services/api';
import type { MealPlan, Recipe } from '../types';
import MealPlanGrid from '../components/MealPlanGrid';

export default function MealPlanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [recipes, setRecipes] = useState<Record<number, Recipe>>({});
  const [loading, setLoading] = useState(true);
  const [swapping, setSwapping] = useState(false);
  const [error, setError] = useState('');

  const loadPlan = useCallback(async () => {
    if (!id) return;
    try {
      const res = await getMealPlan(Number(id));
      setPlan(res.data);
    } catch {
      setError('Failed to load meal plan');
    }
  }, [id]);

  useEffect(() => {
    Promise.all([
      loadPlan(),
      getRecipes().then((res) => {
        const map: Record<number, Recipe> = {};
        res.data.forEach((r) => { map[r.id] = r; });
        setRecipes(map);
      }),
    ])
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [loadPlan]);

  const handleSwap = async (dayIndex: number, mealType: string) => {
    if (!plan || swapping) return;
    setSwapping(true);
    setError('');
    try {
      const res = await swapMeal(plan.id, dayIndex, mealType);
      setPlan(res.data);
    } catch {
      setError('Failed to swap meal. Please try again.');
    } finally {
      setSwapping(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading meal plan...</div>;
  }

  if (!plan) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 mb-4">Meal plan not found.</p>
        <Link to="/meal-plans" className="text-green-600 hover:text-green-800 font-medium">
          &larr; Back to Meal Plans
        </Link>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
        <div>
          <Link to="/meal-plans" className="text-sm text-green-600 hover:text-green-800 mb-1 inline-block">
            &larr; Back to Meal Plans
          </Link>
          <h1 className="text-2xl font-bold text-gray-800">
            Week of {formatDate(plan.week_start)}
          </h1>
        </div>
        <Link
          to={`/grocery/${plan.id}`}
          className="bg-green-600 text-white px-5 py-2 rounded-lg hover:bg-green-700 transition-colors text-center text-sm font-medium"
        >
          View Grocery List
        </Link>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
          {error}
        </div>
      )}

      {/* Swapping indicator */}
      {swapping && (
        <div className="bg-green-50 text-green-700 px-4 py-3 rounded-lg mb-4 text-sm">
          Swapping meal...
        </div>
      )}

      {/* Grid */}
      <MealPlanGrid plan={plan} recipes={recipes} onSwap={handleSwap} />
    </div>
  );
}
