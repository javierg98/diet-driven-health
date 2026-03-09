export interface User {
  id: number;
  username: string;
}

export interface Profile {
  id: number;
  user_id: number;
  skill_level: string;
  health_conditions: string[];
  health_goals: string[];
  dietary_restrictions: string[];
}

export interface Ingredient {
  name: string;
  quantity: number;
  unit: string;
}

export interface Nutrition {
  calories: number;
  protein: number;
  sodium: number;
  potassium: number;
  phosphorus: number;
}

export interface Recipe {
  id: number;
  name: string;
  description: string;
  ingredients: Ingredient[];
  instructions: string[];
  prep_time_minutes: number;
  cook_time_minutes: number;
  difficulty: string;
  servings: number;
  tags: string[];
  autoimmune_score: number;
  nutrition: Nutrition;
  source: string;
}

export interface DayPlan {
  breakfast: number | null;
  lunch: number | null;
  dinner: number | null;
}

export interface MealPlan {
  id: number;
  user_id: number;
  week_start: string;
  days: DayPlan[];
}

export interface DishLog {
  id: number;
  user_id: number;
  recipe_id: number;
  date_cooked: string;
  rating: number;
  notes: string;
  would_make_again: boolean;
}

export interface GroceryItem {
  name: string;
  quantity: number;
  unit: string;
  section: string;
  estimated_cost: number;
  checked: boolean;
}

export interface GroceryList {
  meal_plan_id: number;
  items: GroceryItem[];
  total_estimated_cost: number;
}

export interface FoodEntry {
  id: number;
  user_id: number;
  description: string;
  dish_name: string;
  detected_ingredients: string[];
  created_at: string;
}

export interface FoodPreference {
  id: number;
  user_id: number;
  type: 'like' | 'dislike';
  value: string;
  category: string;
  created_at: string;
}

export interface FoodSubmissionInput {
  text: string;
  submission_type?: 'recipe' | 'past_meals' | 'likes' | 'dislikes' | null;
}

export interface FoodSubmissionResult {
  detected_type: string;
  recipes: Omit<Recipe, 'id'>[];
  entries: { description: string; dish_name: string; detected_ingredients: string[] }[];
  preferences: { type: string; value: string; category: string }[];
}

export interface MealPlanGenerate {
  week_start: string;
  meal_types?: string[];
  cooking_sessions?: number | null;
  weekly_budget?: number | null;
  batch_cooking?: boolean;
}

export interface SkillResults {
  user_preferences: Record<string, unknown> | null;
  user_memory: Record<string, unknown> | null;
  recommendation_weights: Record<string, unknown> | null;
}

export interface WeeklyScore {
  week: string;
  average: number;
  count: number;
}

export interface HealthTrend {
  weekly_scores: WeeklyScore[];
  overall_average: number;
  total_logs: number;
  adherence_percent: number;
}
