# User Profile Builder Skill

Synthesize dish logs, meal plan adherence, and recipe ratings into a comprehensive user memory file.

## When to Use

Run this skill periodically (e.g., weekly) or after a significant number of new dish logs have been recorded. It builds a holistic picture of the user's cooking habits and health trends to improve future recommendations.

## Instructions

1. **Connect to the database** at `backend/diet_driven_health.db` using Python and sqlite3.

2. **Query dish logs with recipe details:**

```sql
SELECT dl.id, dl.date_cooked, dl.rating, dl.notes, dl.would_make_again,
       r.name, r.ingredients, r.tags, r.autoimmune_score, r.difficulty,
       r.prep_time_minutes, r.cook_time_minutes, r.nutrition
FROM dish_logs dl
JOIN recipes r ON dl.recipe_id = r.id
ORDER BY dl.date_cooked DESC;
```

3. **Query meal plan data:**

```sql
SELECT id, week_start, days FROM meal_plans ORDER BY week_start DESC;
```

4. **Query user profile:**

```sql
SELECT skill_level, health_conditions, health_goals, dietary_restrictions
FROM user_profiles LIMIT 1;
```

5. **Analyze and synthesize the following:**

   - **Favorite ingredients:** From recipes that were rated 4-5 and marked would_make_again=true, extract the most common ingredients. Rank by frequency.
   - **Disliked ingredients:** From recipes rated 1-2 or would_make_again=false, extract commonly appearing ingredients. These may be ingredients to avoid in recommendations.
   - **Preferred cuisines:** From top-rated dish logs (rating >= 4), count cuisine tags. Compare against low-rated logs to find clear preferences.
   - **Cooking time preferences:** Compute average total cooking time for highly-rated dishes vs. all dishes. Determine if the user prefers quick meals or is comfortable with longer cook times.
   - **Rating distribution:** Count logs at each rating level (1-5). Compute overall average rating.
   - **Adherence patterns:** For each meal plan, compare the planned recipes in `days` JSON against actual dish logs for that week. Calculate an adherence percentage (dishes cooked / dishes planned). Track this over time to see trends.
   - **Health score trends:** Track average autoimmune_score of cooked recipes over time (group by week or month). Identify whether the user is trending toward higher or lower autoimmune-friendly meals.
   - **Cooking frequency:** Count dish logs per week. Identify most active cooking days.

6. **Write results** to `backend/app/data/user_memory.json` (create the `data/` directory if it does not exist). Use the following JSON structure:

```json
{
  "generated_at": "2026-03-09T12:00:00Z",
  "total_dish_logs": 45,
  "date_range": {"first_log": "2026-01-15", "last_log": "2026-03-08"},
  "favorite_ingredients": [
    {"name": "salmon", "count": 8, "avg_rating": 4.5},
    {"name": "sweet potato", "count": 6, "avg_rating": 4.2}
  ],
  "disliked_ingredients": [
    {"name": "bell pepper", "count": 3, "avg_rating": 2.0}
  ],
  "cuisine_preferences": {
    "preferred": ["mediterranean", "japanese"],
    "avoided": ["thai"]
  },
  "cooking_time": {
    "avg_total_minutes_all": 50,
    "avg_total_minutes_top_rated": 40,
    "prefers_quick_meals": true
  },
  "rating_distribution": {"1": 2, "2": 5, "3": 10, "4": 18, "5": 10},
  "avg_rating": 3.8,
  "adherence": {
    "overall_percentage": 72,
    "weekly_trend": [
      {"week": "2026-02-24", "percentage": 80},
      {"week": "2026-03-03", "percentage": 65}
    ]
  },
  "health_score_trend": {
    "monthly_avg_autoimmune_score": [
      {"month": "2026-01", "avg_score": 3.2},
      {"month": "2026-02", "avg_score": 3.8}
    ],
    "trending": "improving"
  },
  "cooking_frequency": {
    "avg_logs_per_week": 4.5,
    "most_active_days": ["Sunday", "Wednesday"]
  },
  "user_profile": {
    "skill_level": "intermediate",
    "health_conditions": ["lupus", "renal_involvement"],
    "health_goals": ["reduce_inflammation"],
    "dietary_restrictions": ["low_sodium", "gluten_free"]
  }
}
```

7. **Print a summary** to the console: total logs analyzed, top 3 favorite ingredients, adherence trend, health score trend direction, and average rating.

## Notes

- If there are no dish logs, write a minimal JSON with `total_dish_logs: 0` and print a message saying there is not enough data to build a profile.
- Parse all JSON columns (ingredients, tags, nutrition, days) with `json.loads()`.
- For adherence calculation, the `days` column in meal_plans is a JSON object mapping day names to meal data. Count total planned meals and compare against dish_logs that fall within that week's date range.
- The "trending" field under health_score_trend should be "improving" if the most recent month's average is higher than the earliest, "declining" if lower, or "stable" if the difference is less than 0.3.
