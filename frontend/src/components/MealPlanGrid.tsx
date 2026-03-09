import type { MealPlan, Recipe } from '../types';

interface MealPlanGridProps {
  plan: MealPlan;
  recipes: Record<number, Recipe>;
  onSwap: (dayIndex: number, mealType: string) => void;
}

const MEAL_TYPES = ['breakfast', 'lunch', 'dinner'] as const;
const DAY_LABELS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

export default function MealPlanGrid({ plan, recipes, onSwap }: MealPlanGridProps) {
  const getRecipeName = (recipeId: number | null) => {
    if (recipeId === null) return '—';
    return recipes[recipeId]?.name ?? `Recipe #${recipeId}`;
  };

  return (
    <>
      {/* Desktop table layout */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full border-collapse bg-white rounded-lg shadow">
          <thead>
            <tr className="bg-green-600 text-white">
              <th className="px-4 py-3 text-left text-sm font-semibold">Day</th>
              {MEAL_TYPES.map((meal) => (
                <th key={meal} className="px-4 py-3 text-left text-sm font-semibold capitalize">
                  {meal}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {plan.days.map((day, idx) => (
              <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-green-50'}>
                <td className="px-4 py-3 font-medium text-gray-700 border-t">
                  {DAY_LABELS[idx] ?? `Day ${idx + 1}`}
                </td>
                {MEAL_TYPES.map((meal) => {
                  const recipeId = day[meal];
                  return (
                    <td key={meal} className="px-4 py-3 border-t">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm text-gray-800">{getRecipeName(recipeId)}</span>
                        <button
                          onClick={() => onSwap(idx, meal)}
                          className="text-xs text-green-600 hover:text-green-800 hover:bg-green-100 px-2 py-1 rounded transition-colors whitespace-nowrap"
                          title={`Swap ${meal}`}
                        >
                          Swap
                        </button>
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile card layout */}
      <div className="md:hidden space-y-4">
        {plan.days.map((day, idx) => (
          <div key={idx} className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold text-green-700 mb-3">
              {DAY_LABELS[idx] ?? `Day ${idx + 1}`}
            </h3>
            <div className="space-y-2">
              {MEAL_TYPES.map((meal) => {
                const recipeId = day[meal];
                return (
                  <div key={meal} className="flex items-center justify-between bg-green-50 rounded-lg px-3 py-2">
                    <div>
                      <span className="text-xs font-medium text-green-600 uppercase">{meal}</span>
                      <p className="text-sm text-gray-800">{getRecipeName(recipeId)}</p>
                    </div>
                    <button
                      onClick={() => onSwap(idx, meal)}
                      className="text-xs text-green-600 hover:text-green-800 hover:bg-green-200 px-2 py-1 rounded transition-colors"
                    >
                      Swap
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
