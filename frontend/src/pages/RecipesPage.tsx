import { useState, useEffect, useMemo } from 'react';
import { getRecipes } from '../services/api';
import type { Recipe } from '../types';
import RecipeCard from '../components/RecipeCard';

export default function RecipesPage() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [tagFilter, setTagFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [maxTime, setMaxTime] = useState('');
  const [minScore, setMinScore] = useState('');

  useEffect(() => {
    getRecipes()
      .then((res) => setRecipes(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Derive unique tags from recipes
  const allTags = useMemo(() => {
    const tags = new Set<string>();
    recipes.forEach((r) => r.tags.forEach((t) => tags.add(t)));
    return Array.from(tags).sort();
  }, [recipes]);

  const filtered = useMemo(() => {
    return recipes.filter((r) => {
      if (search && !r.name.toLowerCase().includes(search.toLowerCase())) return false;
      if (tagFilter && !r.tags.includes(tagFilter)) return false;
      if (difficultyFilter && r.difficulty !== difficultyFilter) return false;
      if (maxTime && r.prep_time_minutes + r.cook_time_minutes > Number(maxTime)) return false;
      if (minScore && r.autoimmune_score < Number(minScore)) return false;
      return true;
    });
  }, [recipes, search, tagFilter, difficultyFilter, maxTime, minScore]);

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading recipes...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Recipes</h1>

      {/* Search & Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <input
          type="text"
          placeholder="Search recipes..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border rounded-lg px-3 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <select
            value={tagFilter}
            onChange={(e) => setTagFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">All Tags</option>
            {allTags.map((tag) => (
              <option key={tag} value={tag}>{tag}</option>
            ))}
          </select>

          <select
            value={difficultyFilter}
            onChange={(e) => setDifficultyFilter(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">All Difficulties</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>

          <select
            value={maxTime}
            onChange={(e) => setMaxTime(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Any Time</option>
            <option value="30">30 min or less</option>
            <option value="45">45 min or less</option>
            <option value="60">60 min or less</option>
            <option value="90">90 min or less</option>
          </select>

          <select
            value={minScore}
            onChange={(e) => setMinScore(e.target.value)}
            className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Any Score</option>
            <option value="3">3+ Health Score</option>
            <option value="4">4+ Health Score</option>
            <option value="5">5 Health Score</option>
          </select>
        </div>
      </div>

      {/* Results count */}
      <p className="text-sm text-gray-500 mb-4">
        {filtered.length} recipe{filtered.length !== 1 ? 's' : ''} found
      </p>

      {/* Recipe Grid */}
      {filtered.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          No recipes match your filters. Try adjusting your search.
        </div>
      )}
    </div>
  );
}
