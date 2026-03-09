import { useState } from 'react';
import { parseFoodSubmission, saveFoodSubmission, createRecipe } from '../services/api';
import type { FoodSubmissionResult, FoodSubmissionInput } from '../types';

const SUBMISSION_TYPES = [
  { value: '', label: 'Auto-detect' },
  { value: 'recipe', label: 'Recipe' },
  { value: 'past_meals', label: 'Past Meals' },
  { value: 'likes', label: 'Foods I Like' },
  { value: 'dislikes', label: 'Foods I Dislike' },
];

export default function FoodSubmissionPage() {
  const [step, setStep] = useState<'input' | 'review' | 'saved'>('input');
  const [rawText, setRawText] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parseError, setParseError] = useState('');
  const [result, setResult] = useState<FoodSubmissionResult | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  const handleParse = async () => {
    setParsing(true);
    setParseError('');
    try {
      const resp = await parseFoodSubmission({
        text: rawText,
        submission_type: (selectedType || null) as FoodSubmissionInput['submission_type'],
      });
      setResult(resp.data);
      setStep('review');
    } catch {
      setParseError('Failed to parse. Please try again.');
    } finally {
      setParsing(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    setSaving(true);
    setSaveError('');
    try {
      for (const recipe of result.recipes) {
        await createRecipe({ ...recipe, source: 'user_upload' } as any);
      }
      if (result.entries.length > 0 || result.preferences.length > 0) {
        await saveFoodSubmission(result);
      }
      setStep('saved');
    } catch {
      setSaveError('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleRemovePreference = (index: number) => {
    if (!result) return;
    setResult({
      ...result,
      preferences: result.preferences.filter((_, i) => i !== index),
    });
  };

  const handleRemoveEntry = (index: number) => {
    if (!result) return;
    setResult({
      ...result,
      entries: result.entries.filter((_, i) => i !== index),
    });
  };

  if (step === 'saved') {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-green-800 mb-2">Saved!</h2>
          <p className="text-green-600 mb-4">Your food data has been saved and will be used to improve your meal recommendations.</p>
          <button
            onClick={() => { setStep('input'); setRawText(''); setResult(null); setSelectedType(''); }}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Submit More
          </button>
        </div>
      </div>
    );
  }

  if (step === 'review' && result) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Review Submission</h1>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
          <span className="font-medium">Detected type:</span>{' '}
          <span className="capitalize">{result.detected_type.replace('_', ' ')}</span>
        </div>

        {result.recipes.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Recipes</h2>
            {result.recipes.map((recipe, i) => (
              <div key={i} className="border rounded-lg p-4 mb-2">
                <h3 className="font-medium">{recipe.name}</h3>
                <p className="text-sm text-gray-600">{(recipe.ingredients || []).length} ingredients, {(recipe.instructions || []).length} steps</p>
              </div>
            ))}
          </div>
        )}

        {result.preferences.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">
              {result.detected_type === 'dislikes' ? 'Dislikes' : 'Likes'}
            </h2>
            <div className="flex flex-wrap gap-2">
              {result.preferences.map((pref, i) => (
                <span key={i} className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                  pref.type === 'dislike' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                }`}>
                  {pref.value}
                  <button onClick={() => handleRemovePreference(i)} className="ml-2 hover:opacity-70">&times;</button>
                </span>
              ))}
            </div>
          </div>
        )}

        {result.entries.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Past Meals</h2>
            {result.entries.map((entry, i) => (
              <div key={i} className="border rounded-lg p-3 mb-2 flex justify-between items-start">
                <div>
                  <p className="font-medium">{entry.dish_name}</p>
                  <p className="text-sm text-gray-500">
                    Ingredients: {entry.detected_ingredients.join(', ') || 'none detected'}
                  </p>
                </div>
                <button onClick={() => handleRemoveEntry(i)} className="text-red-500 hover:text-red-700">&times;</button>
              </div>
            ))}
          </div>
        )}

        {saveError && <p className="text-red-600 mb-4">{saveError}</p>}

        <div className="flex gap-3">
          <button
            onClick={() => setStep('input')}
            className="border border-gray-300 px-4 py-2 rounded hover:bg-gray-50"
          >
            Back
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">Food Submission</h1>
      <p className="text-gray-600 mb-6">
        Submit recipes, food preferences, past meals, or dislikes. This helps personalize your meal plans.
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Submission Type</label>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2"
        >
          {SUBMISSION_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Content</label>
        <textarea
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          placeholder={
            selectedType === 'recipe'
              ? 'Paste a full recipe with ingredients and instructions...'
              : selectedType === 'past_meals'
              ? "Describe meals you've had recently...\nSalmon with rice and broccoli\nChicken tacos with guacamole"
              : selectedType === 'likes'
              ? 'List foods you enjoy...\nThai curry, avocado, lemon, grilled fish'
              : selectedType === 'dislikes'
              ? 'List foods you want to avoid...\nCilantro, liver, eggplant'
              : 'Paste recipes, list preferences, or describe past meals...'
          }
          rows={10}
          className="w-full border border-gray-300 rounded px-3 py-2 font-mono text-sm"
        />
      </div>

      {parseError && <p className="text-red-600 mb-4">{parseError}</p>}

      <button
        onClick={handleParse}
        disabled={!rawText.trim() || parsing}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
      >
        {parsing ? 'Parsing...' : 'Parse & Review'}
      </button>
    </div>
  );
}
