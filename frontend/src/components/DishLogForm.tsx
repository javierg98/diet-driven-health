import { useState } from 'react';
import { logDish } from '../services/api';
import type { Recipe } from '../types';

interface DishLogFormProps {
  recipes: Recipe[];
  onLogged: () => void;
}

export default function DishLogForm({ recipes, onLogged }: DishLogFormProps) {
  const [recipeId, setRecipeId] = useState<number>(0);
  const [rating, setRating] = useState(0);
  const [notes, setNotes] = useState('');
  const [wouldMakeAgain, setWouldMakeAgain] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipeId) {
      setError('Please select a recipe.');
      return;
    }
    if (!rating) {
      setError('Please select a rating.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      await logDish({ recipe_id: recipeId, rating, notes, would_make_again: wouldMakeAgain });
      setRecipeId(0);
      setRating(0);
      setNotes('');
      setWouldMakeAgain(false);
      onLogged();
    } catch {
      setError('Failed to log dish. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">Log a Dish</h2>

      {error && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded mb-4 text-sm">{error}</div>
      )}

      {/* Recipe select */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Recipe</label>
        <select
          value={recipeId}
          onChange={(e) => setRecipeId(Number(e.target.value))}
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          <option value={0}>Select a recipe...</option>
          {recipes.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
      </div>

      {/* Rating */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Rating</label>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              className="text-2xl focus:outline-none transition-colors"
              aria-label={`Rate ${star} star${star > 1 ? 's' : ''}`}
            >
              {star <= rating ? (
                <span className="text-yellow-400">&#9733;</span>
              ) : (
                <span className="text-gray-300">&#9733;</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Notes */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={3}
          placeholder="How did it turn out? Any modifications?"
          className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
        />
      </div>

      {/* Would make again */}
      <div className="mb-4 flex items-center gap-2">
        <button
          type="button"
          onClick={() => setWouldMakeAgain(!wouldMakeAgain)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            wouldMakeAgain ? 'bg-green-500' : 'bg-gray-300'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              wouldMakeAgain ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
        <span className="text-sm text-gray-700">Would make again</span>
      </div>

      <button
        type="submit"
        disabled={submitting}
        className="w-full bg-green-600 text-white py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
      >
        {submitting ? 'Logging...' : 'Log Dish'}
      </button>
    </form>
  );
}
