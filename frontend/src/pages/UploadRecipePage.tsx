import { useState } from 'react';
import { Link } from 'react-router-dom';
import { parseRecipeText, createRecipe } from '../services/api';
import type { Ingredient, Nutrition } from '../types';

function TagInput({ label, tags, onAdd, onRemove, placeholder }: {
  label: string;
  tags: string[];
  onAdd: (tag: string) => void;
  onRemove: (tag: string) => void;
  placeholder?: string;
}) {
  const [input, setInput] = useState('');

  const handleAdd = () => {
    const trimmed = input.trim().toLowerCase();
    if (trimmed && !tags.includes(trimmed)) {
      onAdd(trimmed);
      setInput('');
    }
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <div className="flex gap-2 mb-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd(); } }}
          placeholder={placeholder}
          className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button
          type="button"
          onClick={handleAdd}
          className="bg-green-600 text-white px-4 py-2 rounded text-sm hover:bg-green-700"
        >
          Add
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center bg-green-100 text-green-800 text-sm px-3 py-1 rounded-full"
          >
            {tag}
            <button
              type="button"
              onClick={() => onRemove(tag)}
              className="ml-1.5 text-green-600 hover:text-green-900 font-bold"
            >
              &times;
            </button>
          </span>
        ))}
      </div>
    </div>
  );
}

const emptyNutrition: Nutrition = {
  calories: 0,
  protein: 0,
  sodium: 0,
  potassium: 0,
  phosphorus: 0,
};

export default function UploadRecipePage() {
  // Step tracking
  const [step, setStep] = useState<'paste' | 'review' | 'saved'>('paste');

  // Paste step
  const [rawText, setRawText] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parseError, setParseError] = useState('');

  // Review step (editable fields)
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [instructions, setInstructions] = useState<string[]>([]);
  const [prepTime, setPrepTime] = useState(0);
  const [cookTime, setCookTime] = useState(0);
  const [difficulty, setDifficulty] = useState('easy');
  const [servings, setServings] = useState(1);
  const [tags, setTags] = useState<string[]>([]);
  const [autoimmuneScore, setAutoimmuneScore] = useState(5);
  const [nutrition, setNutrition] = useState<Nutrition>(emptyNutrition);
  const [source, setSource] = useState('user_upload');

  // Save step
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');
  const [savedId, setSavedId] = useState<number | null>(null);

  const handleParse = async () => {
    if (!rawText.trim()) return;
    setParsing(true);
    setParseError('');
    try {
      const res = await parseRecipeText(rawText);
      const r = res.data;
      setName(r.name || '');
      setDescription(r.description || '');
      setIngredients(r.ingredients || []);
      setInstructions(r.instructions || []);
      setPrepTime(r.prep_time_minutes || 0);
      setCookTime(r.cook_time_minutes || 0);
      setDifficulty(r.difficulty || 'easy');
      setServings(r.servings || 1);
      setTags(r.tags || []);
      setAutoimmuneScore(r.autoimmune_score ?? 5);
      setNutrition(r.nutrition || emptyNutrition);
      setSource(r.source || 'user_upload');
      setStep('review');
    } catch {
      setParseError('Failed to parse recipe. Please check the text and try again.');
    } finally {
      setParsing(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveError('');
    try {
      const res = await createRecipe({
        name,
        description,
        ingredients,
        instructions,
        prep_time_minutes: prepTime,
        cook_time_minutes: cookTime,
        difficulty,
        servings,
        tags,
        autoimmune_score: autoimmuneScore,
        nutrition,
        source,
      });
      setSavedId(res.data.id);
      setStep('saved');
    } catch {
      setSaveError('Failed to save recipe. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  // Ingredient helpers
  const updateIngredient = (index: number, field: keyof Ingredient, value: string | number) => {
    setIngredients((prev) =>
      prev.map((ing, i) => (i === index ? { ...ing, [field]: value } : ing))
    );
  };

  const removeIngredient = (index: number) => {
    setIngredients((prev) => prev.filter((_, i) => i !== index));
  };

  const addIngredient = () => {
    setIngredients((prev) => [...prev, { name: '', quantity: 1, unit: '' }]);
  };

  // Instruction helpers
  const updateInstruction = (index: number, value: string) => {
    setInstructions((prev) => prev.map((inst, i) => (i === index ? value : inst)));
  };

  const removeInstruction = (index: number) => {
    setInstructions((prev) => prev.filter((_, i) => i !== index));
  };

  const addInstruction = () => {
    setInstructions((prev) => [...prev, '']);
  };

  // Nutrition helper
  const updateNutrition = (field: keyof Nutrition, value: number) => {
    setNutrition((prev) => ({ ...prev, [field]: value }));
  };

  // --- PASTE STEP ---
  if (step === 'paste') {
    return (
      <div className="max-w-2xl mx-auto">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Upload Recipe</h1>
        <p className="text-gray-500 mb-6">
          Paste a recipe from any source and we'll parse it into structured fields for you.
        </p>

        {parseError && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {parseError}
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Recipe Text</label>
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste your recipe here... Include the name, ingredients, instructions, and any other details."
              rows={12}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-y"
            />
          </div>

          <button
            onClick={handleParse}
            disabled={parsing || !rawText.trim()}
            className="w-full bg-green-600 text-white py-2.5 rounded font-medium hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {parsing ? (
              <>
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Parsing...
              </>
            ) : (
              'Parse Recipe'
            )}
          </button>
        </div>
      </div>
    );
  }

  // --- SAVED STEP ---
  if (step === 'saved') {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="bg-green-50 border border-green-200 text-green-700 px-6 py-8 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-2">Recipe Saved!</h2>
          <p className="mb-6 text-green-600">
            "{name}" has been added to your recipe collection.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to={`/recipes/${savedId}`}
              className="bg-green-600 text-white px-6 py-2.5 rounded font-medium hover:bg-green-700"
            >
              View Recipe
            </Link>
            <button
              onClick={() => {
                setStep('paste');
                setRawText('');
                setSavedId(null);
              }}
              className="border border-green-600 text-green-700 px-6 py-2.5 rounded font-medium hover:bg-green-50"
            >
              Upload Another
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- REVIEW STEP ---
  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Review Recipe</h1>
          <p className="text-gray-500 text-sm mt-1">Edit any fields before saving.</p>
        </div>
        <button
          onClick={() => setStep('paste')}
          className="text-sm text-gray-500 hover:text-green-700 underline"
        >
          Back to Paste
        </button>
      </div>

      {saveError && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {saveError}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-y"
          />
        </div>

        {/* Ingredients */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Ingredients</label>
          <div className="space-y-2">
            {ingredients.map((ing, i) => (
              <div key={i} className="flex gap-2 items-center">
                <input
                  type="text"
                  value={ing.name}
                  onChange={(e) => updateIngredient(i, 'name', e.target.value)}
                  placeholder="Name"
                  className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <input
                  type="number"
                  value={ing.quantity}
                  onChange={(e) => updateIngredient(i, 'quantity', parseFloat(e.target.value) || 0)}
                  placeholder="Qty"
                  className="w-20 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <input
                  type="text"
                  value={ing.unit}
                  onChange={(e) => updateIngredient(i, 'unit', e.target.value)}
                  placeholder="Unit"
                  className="w-24 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
                <button
                  type="button"
                  onClick={() => removeIngredient(i)}
                  className="text-red-400 hover:text-red-600 font-bold text-lg px-1"
                  title="Remove ingredient"
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addIngredient}
            className="mt-2 text-sm text-green-600 hover:text-green-800 font-medium"
          >
            + Add Ingredient
          </button>
        </div>

        {/* Instructions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Instructions</label>
          <div className="space-y-2">
            {instructions.map((inst, i) => (
              <div key={i} className="flex gap-2 items-start">
                <span className="text-sm text-gray-400 mt-2 w-6 text-right shrink-0">{i + 1}.</span>
                <textarea
                  value={inst}
                  onChange={(e) => updateInstruction(i, e.target.value)}
                  rows={2}
                  className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-y"
                />
                <button
                  type="button"
                  onClick={() => removeInstruction(i)}
                  className="text-red-400 hover:text-red-600 font-bold text-lg px-1 mt-1"
                  title="Remove step"
                >
                  &times;
                </button>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={addInstruction}
            className="mt-2 text-sm text-green-600 hover:text-green-800 font-medium"
          >
            + Add Step
          </button>
        </div>

        {/* Grid: prep time, cook time, difficulty, servings, autoimmune score */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Prep Time (min)</label>
            <input
              type="number"
              value={prepTime}
              onChange={(e) => setPrepTime(parseInt(e.target.value) || 0)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Cook Time (min)</label>
            <input
              type="number"
              value={cookTime}
              onChange={(e) => setCookTime(parseInt(e.target.value) || 0)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Servings</label>
            <input
              type="number"
              value={servings}
              onChange={(e) => setServings(parseInt(e.target.value) || 1)}
              min={1}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Autoimmune Score</label>
            <input
              type="number"
              value={autoimmuneScore}
              onChange={(e) => setAutoimmuneScore(parseInt(e.target.value) || 0)}
              min={0}
              max={10}
              className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Nutrition */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Nutrition (per serving)</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {(Object.keys(nutrition) as Array<keyof Nutrition>).map((key) => (
              <div key={key}>
                <label className="block text-xs text-gray-500 mb-0.5 capitalize">{key}</label>
                <input
                  type="number"
                  value={nutrition[key]}
                  onChange={(e) => updateNutrition(key, parseFloat(e.target.value) || 0)}
                  className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Tags */}
        <TagInput
          label="Tags"
          tags={tags}
          onAdd={(tag) => setTags((prev) => [...prev, tag])}
          onRemove={(tag) => setTags((prev) => prev.filter((t) => t !== tag))}
          placeholder="e.g. anti-inflammatory, dinner, quick"
        />

        {/* Save */}
        <button
          onClick={handleSave}
          disabled={saving || !name.trim()}
          className="w-full bg-green-600 text-white py-2.5 rounded font-medium hover:bg-green-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Save Recipe'}
        </button>
      </div>
    </div>
  );
}
