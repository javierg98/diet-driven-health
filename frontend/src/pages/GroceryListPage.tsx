import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getGroceryList } from '../services/api';
import type { GroceryItem } from '../types';

const SECTION_ORDER = ['produce', 'protein', 'dairy', 'grains', 'pantry', 'frozen', 'other'];

const SECTION_LABELS: Record<string, string> = {
  produce: 'Produce',
  protein: 'Protein',
  dairy: 'Dairy',
  grains: 'Grains',
  pantry: 'Pantry',
  frozen: 'Frozen',
  other: 'Other',
};

const SECTION_COLORS: Record<string, string> = {
  produce: 'bg-green-100 text-green-800',
  protein: 'bg-red-100 text-red-800',
  dairy: 'bg-blue-100 text-blue-800',
  grains: 'bg-amber-100 text-amber-800',
  pantry: 'bg-orange-100 text-orange-800',
  frozen: 'bg-cyan-100 text-cyan-800',
  other: 'bg-gray-100 text-gray-800',
};

type CheckedGroceryItem = GroceryItem & { _idx: number };

export default function GroceryListPage() {
  const { planId } = useParams();
  const [items, setItems] = useState<GroceryItem[]>([]);
  const [checkedSet, setCheckedSet] = useState<Set<number>>(new Set());
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (planId) {
      getGroceryList(Number(planId))
        .then((res) => {
          setItems(res.data.items);
          setTotal(res.data.total_estimated_cost);
          setLoading(false);
        })
        .catch(() => {
          setError('Failed to load grocery list.');
          setLoading(false);
        });
    }
  }, [planId]);

  const toggleItem = (idx: number) => {
    setCheckedSet((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  };

  const toggleSection = (section: string) => {
    setCollapsedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  // Group items by section, preserving original index
  const sections: Record<string, CheckedGroceryItem[]> = {};
  items.forEach((item, idx) => {
    const key = item.section || 'other';
    if (!sections[key]) sections[key] = [];
    sections[key].push({ ...item, _idx: idx });
  });

  const orderedSections = SECTION_ORDER.filter((s) => sections[s]);
  // Add any sections not in the predefined order
  Object.keys(sections).forEach((s) => {
    if (!orderedSections.includes(s)) orderedSections.push(s);
  });

  const checkedCount = checkedSet.size;
  const totalCount = items.length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading grocery list...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
          {error}
        </div>
        <Link
          to={`/meal-plans/${planId}`}
          className="inline-block mt-4 text-green-600 hover:text-green-800 font-medium"
        >
          &larr; Back to Meal Plan
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4 pb-28">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link
            to={`/meal-plans/${planId}`}
            className="text-green-600 hover:text-green-800 text-sm font-medium"
          >
            &larr; Back to Meal Plan
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-1">Grocery List</h1>
          <p className="text-sm text-gray-500 mt-1">
            {checkedCount} of {totalCount} items checked
          </p>
        </div>
      </div>

      {/* Sections */}
      {totalCount === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No grocery items found for this meal plan.
        </div>
      ) : (
        <div className="space-y-4">
          {orderedSections.map((sectionKey) => {
            const sectionItems = sections[sectionKey];
            const isCollapsed = collapsedSections.has(sectionKey);
            const sectionCheckedCount = sectionItems.filter((i) => checkedSet.has(i._idx)).length;
            const colorClass = SECTION_COLORS[sectionKey] || SECTION_COLORS.other;
            const label = SECTION_LABELS[sectionKey] || sectionKey.charAt(0).toUpperCase() + sectionKey.slice(1);

            return (
              <div key={sectionKey} className="rounded-lg border border-gray-200 overflow-hidden">
                {/* Section Header */}
                <button
                  onClick={() => toggleSection(sectionKey)}
                  className={`w-full flex items-center justify-between px-4 py-3 ${colorClass} font-semibold text-sm uppercase tracking-wide`}
                >
                  <span>
                    {label} ({sectionCheckedCount}/{sectionItems.length})
                  </span>
                  <svg
                    className={`w-5 h-5 transition-transform ${isCollapsed ? '' : 'rotate-180'}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Section Items */}
                {!isCollapsed && (
                  <ul className="divide-y divide-gray-100">
                    {sectionItems.map((item) => {
                      const isChecked = checkedSet.has(item._idx);
                      return (
                        <li key={item._idx}>
                          <label
                            className={`flex items-center gap-4 px-4 py-3 cursor-pointer active:bg-gray-50 select-none min-h-[52px] ${
                              isChecked ? 'bg-gray-50' : ''
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => toggleItem(item._idx)}
                              className="w-6 h-6 rounded border-gray-300 text-green-600 focus:ring-green-500 flex-shrink-0 cursor-pointer"
                            />
                            <div className={`flex-1 min-w-0 ${isChecked ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                              <span className="font-medium">{item.name}</span>
                              <span className="ml-2 text-sm text-gray-500">
                                {item.quantity} {item.unit}
                              </span>
                            </div>
                            <span className={`text-sm font-medium flex-shrink-0 ${isChecked ? 'text-gray-400' : 'text-gray-700'}`}>
                              ${item.estimated_cost.toFixed(2)}
                            </span>
                          </label>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Sticky Total Bar */}
      {totalCount > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg px-4 py-4 z-50">
          <div className="max-w-2xl mx-auto flex items-center justify-between">
            <div>
              <span className="text-sm text-gray-500">Estimated Total</span>
              <p className="text-2xl font-bold text-green-700">${total.toFixed(2)}</p>
            </div>
            <div className="text-right">
              <span className="text-sm text-gray-500">Progress</span>
              <p className="text-lg font-semibold text-gray-700">{checkedCount}/{totalCount}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
