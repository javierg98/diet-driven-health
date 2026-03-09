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
  breakfast: number;
  lunch: number;
  dinner: number;
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
