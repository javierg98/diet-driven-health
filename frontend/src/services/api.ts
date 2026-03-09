import axios from 'axios';
import type {
  User, Profile, Recipe, MealPlan, DishLog, GroceryList,
  FoodSubmissionInput, FoodSubmissionResult, FoodPreference, FoodEntry,
  MealPlanGenerate, SkillResults, HealthTrend,
} from '../types';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (username: string, password: string) =>
  api.post<User>('/auth/register', { username, password });

export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  const resp = await api.post<{ access_token: string }>('/auth/login', params);
  localStorage.setItem('token', resp.data.access_token);
  return resp.data;
};

export const getMe = () => api.get<User>('/auth/me');

export const logout = () => localStorage.removeItem('token');

// Profile
export const getProfile = () => api.get<Profile>('/profile');
export const createProfile = (data: Omit<Profile, 'id' | 'user_id'>) =>
  api.post<Profile>('/profile', data);
export const updateProfile = (data: Omit<Profile, 'id' | 'user_id'>) =>
  api.put<Profile>('/profile', data);

// Recipes
export const getRecipes = (params?: Record<string, string>) =>
  api.get<Recipe[]>('/recipes', { params });
export const getRecipe = (id: number) => api.get<Recipe>(`/recipes/${id}`);
export const createRecipe = (data: Omit<Recipe, 'id'>) =>
  api.post<Recipe>('/recipes', data);

// Meal Plans
export const generateMealPlan = (data: MealPlanGenerate) =>
  api.post<MealPlan>('/meal-plans/generate', data);
export const getMealPlans = () => api.get<MealPlan[]>('/meal-plans');
export const getMealPlan = (id: number) => api.get<MealPlan>(`/meal-plans/${id}`);
export const swapMeal = (planId: number, dayIndex: number, mealType: string) =>
  api.put<MealPlan>(`/meal-plans/${planId}/swap`, { day_index: dayIndex, meal_type: mealType });

// Dish Log
export const logDish = (data: Omit<DishLog, 'id' | 'user_id' | 'date_cooked'>) =>
  api.post<DishLog>('/dish-log', data);
export const getDishLogs = () => api.get<DishLog[]>('/dish-log');
export const getFavorites = () => api.get<DishLog[]>('/dish-log/favorites');

// Grocery
export const getGroceryList = (planId: number) =>
  api.get<GroceryList>(`/grocery/${planId}`);

// Upload
export const parseRecipeText = (text: string) =>
  api.post<Recipe>('/upload/parse', { text });

// Food Submission
export const parseFoodSubmission = (data: FoodSubmissionInput) =>
  api.post<FoodSubmissionResult>('/food/parse', data);
export const saveFoodSubmission = (data: FoodSubmissionResult) =>
  api.post('/food/save', data);
export const getFoodPreferences = () =>
  api.get<FoodPreference[]>('/food/preferences');
export const getFoodEntries = () =>
  api.get<FoodEntry[]>('/food/entries');

// Admin
export const getSkillResults = () =>
  api.get<SkillResults>('/admin/skill-results');
export const getHealthTrend = () =>
  api.get<HealthTrend>('/admin/health-trend');

export default api;
