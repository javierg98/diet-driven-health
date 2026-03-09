import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getRecipe } from '../services/api';
import type { Recipe } from '../types';

const difficultyColors: Record<string, string> = {
  beginner: 'bg-blue-100 text-blue-800',
  intermediate: 'bg-yellow-100 text-yellow-800',
  advanced: 'bg-red-100 text-red-800',
};

function ScoreDots({ score, max = 5 }: { score: number; max?: number }) {
  return (
    <div className="flex gap-1 items-center">
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={`inline-block w-3 h-3 rounded-full ${
            i < score ? 'bg-green-500' : 'bg-gray-200'
          }`}
        />
      ))}
      <span className="ml-1 text-sm text-gray-600">{score}/{max}</span>
    </div>
  );
}

export default function RecipeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    getRecipe(Number(id))
      .then((res) => setRecipe(res.data))
      .catch(() => setError('Recipe not found.'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading recipe...</div>;
  }

  if (error || !recipe) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">{error || 'Recipe not found.'}</p>
        <Link to="/recipes" className="text-green-600 hover:underline">Back to recipes</Link>
      </div>
    );
  }

  const totalTime = recipe.prep_time_minutes + recipe.cook_time_minutes;
  const diffClass = difficultyColors[recipe.difficulty] || 'bg-gray-100 text-gray-800';

  return (
    <div>
      <Link to="/recipes" className="text-green-600 hover:underline text-sm mb-4 inline-block">
        &larr; Back to recipes
      </Link>

      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{recipe.name}</h1>
        <p className="text-gray-600 mb-4">{recipe.description}</p>

        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Meta */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-500 block">Difficulty</span>
            <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium mt-1 ${diffClass}`}>
              {recipe.difficulty}
            </span>
          </div>
          <div>
            <span className="text-gray-500 block">Total Time</span>
            <span className="font-medium">{totalTime} min</span>
            <span className="text-gray-400 text-xs block">
              ({recipe.prep_time_minutes} prep + {recipe.cook_time_minutes} cook)
            </span>
          </div>
          <div>
            <span className="text-gray-500 block">Servings</span>
            <span className="font-medium">{recipe.servings}</span>
          </div>
          <div>
            <span className="text-gray-500 block">Health Score</span>
            <ScoreDots score={recipe.autoimmune_score} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ingredients */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Ingredients</h2>
          <ul className="space-y-2">
            {recipe.ingredients.map((ing, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <span className="text-green-500 mt-0.5">&#x2022;</span>
                <span>
                  <span className="font-medium">{ing.quantity} {ing.unit}</span>{' '}
                  {ing.name}
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Instructions */}
        <div className="bg-white rounded-lg shadow p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Instructions</h2>
          <ol className="space-y-3">
            {recipe.instructions.map((step, i) => (
              <li key={i} className="flex gap-3 text-sm">
                <span className="flex-shrink-0 w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </span>
                <span className="text-gray-700 leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      </div>

      {/* Nutrition */}
      <div className="bg-white rounded-lg shadow p-6 mt-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-3">Nutritional Breakdown</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-green-50">
                <th className="px-4 py-2 text-left text-green-700">Nutrient</th>
                <th className="px-4 py-2 text-right text-green-700">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t">
                <td className="px-4 py-2">Calories</td>
                <td className="px-4 py-2 text-right font-medium">{recipe.nutrition.calories} kcal</td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-2">Protein</td>
                <td className="px-4 py-2 text-right font-medium">{recipe.nutrition.protein} g</td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-2">Sodium</td>
                <td className="px-4 py-2 text-right font-medium">{recipe.nutrition.sodium} mg</td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-2">Potassium</td>
                <td className="px-4 py-2 text-right font-medium">{recipe.nutrition.potassium} mg</td>
              </tr>
              <tr className="border-t">
                <td className="px-4 py-2">Phosphorus</td>
                <td className="px-4 py-2 text-right font-medium">{recipe.nutrition.phosphorus} mg</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Source */}
      {recipe.source && (
        <p className="text-xs text-gray-400 mt-4">Source: {recipe.source}</p>
      )}
    </div>
  );
}
