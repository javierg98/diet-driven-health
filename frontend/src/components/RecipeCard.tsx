import { Link } from 'react-router-dom';
import type { Recipe } from '../types';

const difficultyColors: Record<string, string> = {
  beginner: 'bg-blue-100 text-blue-800',
  intermediate: 'bg-yellow-100 text-yellow-800',
  advanced: 'bg-red-100 text-red-800',
};

function ScoreDots({ score, max = 5 }: { score: number; max?: number }) {
  return (
    <div className="flex gap-1">
      {Array.from({ length: max }, (_, i) => (
        <span
          key={i}
          className={`inline-block w-2.5 h-2.5 rounded-full ${
            i < score ? 'bg-green-500' : 'bg-gray-200'
          }`}
        />
      ))}
    </div>
  );
}

export default function RecipeCard({ recipe }: { recipe: Recipe }) {
  const totalTime = recipe.prep_time_minutes + recipe.cook_time_minutes;
  const diffClass = difficultyColors[recipe.difficulty] || 'bg-gray-100 text-gray-800';

  return (
    <Link
      to={`/recipes/${recipe.id}`}
      className="block bg-white rounded-lg shadow hover:shadow-md transition-shadow"
    >
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-1">{recipe.name}</h3>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-3">
          {recipe.tags.map((tag) => (
            <span
              key={tag}
              className="text-xs px-2 py-0.5 rounded-full bg-green-100 text-green-800"
            >
              {tag}
            </span>
          ))}
        </div>

        {/* Meta row */}
        <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${diffClass}`}>
            {recipe.difficulty}
          </span>
          <span>{totalTime} min</span>
        </div>

        {/* Score */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Health score</span>
          <ScoreDots score={recipe.autoimmune_score} />
          <span className="text-xs text-gray-500">{recipe.autoimmune_score}/5</span>
        </div>
      </div>
    </Link>
  );
}
