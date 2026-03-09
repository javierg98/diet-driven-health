# Recommender V2 — Design Document

**Date:** 2026-03-09
**Status:** Approved

## Overview

Three interconnected improvements to Diet Driven Health:

1. **Weighted scoring recommender** with weekly goal inputs (replaces random shuffle)
2. **Unified food submission page** (replaces recipe-only upload)
3. **Admin console** for viewing skill analysis results + health trends

## 1. Weekly Plan Goals & Scoring Engine

### Weekly Generation Input

When generating a meal plan, the user provides:

- **Week start date** (existing)
- **Meal types to plan** — checkboxes: breakfast, lunch, dinner (default: all)
- **Cooking sessions available** — number: "How many times can you cook this week?"
- **Weekly grocery budget** — optional dollar amount
- **Batch cooking preference** — toggle: "Plan leftovers to reduce cooking sessions"

### Scoring Engine

Each candidate recipe is scored 0–100. **No recipes are excluded** — lower-scoring recipes appear less often. This is harm reduction, not restriction.

| Dimension | Weight | Logic |
|-----------|--------|-------|
| Preference match | 0.30 | Ingredients/cuisines from user's likes; penalize dislikes |
| Ingredient overlap | 0.20 | Bonus for sharing ingredients with already-planned meals (reduces waste) |
| Cost efficiency | 0.15 | Lower estimated cost → higher score; uses purchase-unit costs |
| Autoimmune friendliness | 0.15 | Higher `autoimmune_score` → higher score, soft preference only |
| Cooking time fit | 0.10 | Fits within user's available time per session |
| Variety | 0.10 | Penalize repeating cuisines/proteins within the week |

Default weights are starting points. The `meal-plan-optimizer` skill adjusts them based on user behavior.

### Plan Building Algorithm

1. Score all eligible recipes for each meal slot (filtered by selected meal types only — no hard exclusions)
2. If batch cooking on: after selecting a dinner, duplicate as next day's lunch (1 cooking session)
3. Track ingredient accumulator — each recipe added boosts overlap scores for recipes sharing those ingredients
4. Enforce cooking session limit: once reached, remaining slots filled with leftover/no-cook options
5. If budget set: running cost tracked, deprioritize expensive recipes as budget fills

### Purchase-Unit Cost Model

- Each ingredient maps to a **purchase unit** (e.g., strawberries → "1 pint, ~$4", rice → "2lb bag, ~$3")
- When multiple meals share an ingredient, the purchase cost is amortized across those meals
- Rough estimation now; store-specific pricing planned for later

### Health Trend Visibility

- After each week, calculate average `autoimmune_score` of dishes actually logged
- Show **trend line** on dashboard: weekly average autoimmune score over time
- Framing: "Your meals this week averaged 3.8/5 for autoimmune friendliness — up from 3.2 last month"
- No guilt, no hard targets — just visibility
- The `meal-plan-optimizer` skill observes this trend and gently adjusts autoimmune weight

## 2. Unified Food Submission Page

Replaces the recipe-only upload with a flexible input that handles recipes, preferences, past meals, and dislikes.

### Submission Types

| Type | Example Input | Stored As |
|------|--------------|-----------|
| Recipe | Full recipe with ingredients & instructions | `Recipe` (existing, `source="user_upload"`) |
| Past meals | "Salmon with rice and broccoli, chicken tacos" | `FoodEntry` records |
| Likes | "Thai curry, avocado, lemon, grilled fish" | `FoodPreference` with `type="like"` |
| Dislikes | "Cilantro, liver, eggplant" | `FoodPreference` with `type="dislike"` |

### Auto-Detection with Override

- Parser detects type from content (ingredients + instructions = recipe; comma list = preferences; descriptive = past meals)
- User can override via type selector
- Review step shows extracted data — user confirms or edits before saving

### New Data Models

**FoodEntry** (past meals):
- `id`, `user_id`, `description` (original text), `dish_name`, `detected_ingredients` (JSON list), `created_at`

**FoodPreference** (likes/dislikes):
- `id`, `user_id`, `type` ("like" | "dislike"), `value` (the item), `category` ("ingredient" | "cuisine" | "dish" | "flavor"), `created_at`

### Effect on Recommender

- **Likes** boost preference match scores for matching recipes
- **Dislikes** penalize matching recipes (soft penalty, not exclusion)
- **Past meals** inform skills — detected ingredients build taste profile
- Submissions create an increasingly personalized taste profile over time

### Frontend Flow

1. Select type (or let auto-detect handle it)
2. Paste/type content in text area
3. Parse — backend extracts structured data
4. Review — edit extracted data (recipe: full editor; preferences: tag list; past meals: dishes + ingredients)
5. Save

## 3. Admin Console & Skill Integration

### Admin Page (`/admin`)

Protected page (same auth) with two panels:

**Panel 1: Skill Results Dashboard**
- Displays latest output from each skill (`user_preferences.json`, `user_memory.json`, `recommendation_weights.json`)
- Shows: last run timestamp, key metrics (top ingredients, cuisines, current weights, adherence %, health trend)
- Read-only view of what the recommendation engine "knows"

**Panel 2: Health Trend Overview**
- Rolling autoimmune score trend line with detail
- Weekly adherence rate (% of planned meals actually logged)
- Weight adjustment history — what the optimizer changed and why

### Skill Triggering

Skills remain triggered from Claude Code CLI. Workflow:

1. Run a skill in Claude Code (e.g., `/recipe-analyzer`)
2. Skill reads DB, analyzes, writes updated JSON to `backend/app/data/`
3. `/admin` page loads latest JSON files and displays results
4. Recommender reads JSON files at plan generation time

### Updated Skill Responsibilities

| Skill | Reads | Writes | Effect |
|-------|-------|--------|--------|
| recipe-analyzer | Recipes + FoodEntries + FoodPreferences | `user_preferences.json` | Builds taste profile from all food data |
| user-profile-builder | Dish logs, adherence, ratings, food entries | `user_memory.json` | Tracks behavior, frequency, health trends |
| meal-plan-optimizer | `user_memory.json`, recent logs | `recommendation_weights.json` | Adjusts scoring weights based on trends |

### Data Flow

```
User submits food data (recipes, preferences, past meals)
    → Stored in DB
Developer runs skills in Claude Code CLI
    → Skills analyze DB → write JSON files
/admin page displays latest analysis
    → Recommender reads JSON at generation time
    → Smarter, more personalized meal plans
```
