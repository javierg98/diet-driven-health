import { useState, useEffect } from 'react';
import { getProfile, createProfile, updateProfile } from '../services/api';

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

export default function ProfilePage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isNew, setIsNew] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [error, setError] = useState('');

  const [skillLevel, setSkillLevel] = useState('intermediate');
  const [healthConditions, setHealthConditions] = useState<string[]>([]);
  const [healthGoals, setHealthGoals] = useState<string[]>([]);
  const [dietaryRestrictions, setDietaryRestrictions] = useState<string[]>([]);

  useEffect(() => {
    getProfile()
      .then((res) => {
        const p = res.data;
        setSkillLevel(p.skill_level);
        setHealthConditions(p.health_conditions);
        setHealthGoals(p.health_goals);
        setDietaryRestrictions(p.dietary_restrictions);
        setIsNew(false);
        setLoading(false);
      })
      .catch((err) => {
        if (err.response?.status === 404) {
          setIsNew(true);
        } else {
          setError('Failed to load profile.');
        }
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSuccessMsg('');
    setError('');
    const data = {
      skill_level: skillLevel,
      health_conditions: healthConditions,
      health_goals: healthGoals,
      dietary_restrictions: dietaryRestrictions,
    };
    try {
      if (isNew) {
        await createProfile(data);
        setIsNew(false);
        setSuccessMsg('Profile created successfully!');
      } else {
        await updateProfile(data);
        setSuccessMsg('Profile updated successfully!');
      }
    } catch {
      setError('Failed to save profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12 text-gray-500">Loading profile...</div>;
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-2">
        {isNew ? 'Set Up Your Profile' : 'Your Profile'}
      </h1>
      {isNew && (
        <p className="text-gray-500 mb-6">
          Welcome! Fill in your preferences to get personalized meal recommendations.
        </p>
      )}

      {successMsg && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
          {successMsg}
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Skill Level */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Cooking Skill Level</label>
          <select
            value={skillLevel}
            onChange={(e) => setSkillLevel(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        {/* Health Conditions */}
        <TagInput
          label="Health Conditions"
          tags={healthConditions}
          onAdd={(tag) => setHealthConditions((prev) => [...prev, tag])}
          onRemove={(tag) => setHealthConditions((prev) => prev.filter((t) => t !== tag))}
          placeholder="e.g. lupus, renal"
        />

        {/* Health Goals */}
        <TagInput
          label="Health Goals"
          tags={healthGoals}
          onAdd={(tag) => setHealthGoals((prev) => [...prev, tag])}
          onRemove={(tag) => setHealthGoals((prev) => prev.filter((t) => t !== tag))}
          placeholder="e.g. anti-inflammatory, kidney-friendly"
        />

        {/* Dietary Restrictions */}
        <TagInput
          label="Dietary Restrictions"
          tags={dietaryRestrictions}
          onAdd={(tag) => setDietaryRestrictions((prev) => [...prev, tag])}
          onRemove={(tag) => setDietaryRestrictions((prev) => prev.filter((t) => t !== tag))}
          placeholder="e.g. low-sodium, low-potassium, gluten-free"
        />

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full bg-green-600 text-white py-2.5 rounded font-medium hover:bg-green-700 disabled:opacity-50"
        >
          {saving ? 'Saving...' : isNew ? 'Create Profile' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}
