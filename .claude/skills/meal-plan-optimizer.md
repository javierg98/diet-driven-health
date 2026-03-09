# Meal Plan Optimizer Skill

Analyze user behavior data to suggest improved scoring weights for the meal plan recommender.

## When to Use

Run this skill after the User Profile Builder skill has been run at least once (so that `backend/app/data/user_memory.json` exists). Use it to tune the recommendation engine based on actual user behavior rather than default weights.

## Instructions

1. **Read the user memory file** at `backend/app/data/user_memory.json`. If it does not exist, print an error message saying to run the User Profile Builder skill first and stop.

2. **Read current weights** from `backend/app/data/recommendation_weights.json` if it exists. If it does not exist, start with these defaults:

```json
{
  "autoimmune_score": 0.30,
  "user_rating_history": 0.25,
  "ingredient_preference": 0.20,
  "cuisine_match": 0.10,
  "cooking_time_fit": 0.10,
  "variety_bonus": 0.05
}
```

3. **Connect to the database** at `backend/diet_driven_health.db` using Python and sqlite3.

4. **Query recent dish logs** (last 30 days) to understand current behavior:

```sql
SELECT dl.rating, dl.would_make_again, r.autoimmune_score, r.difficulty,
       r.tags, r.prep_time_minutes, r.cook_time_minutes
FROM dish_logs dl
JOIN recipes r ON dl.recipe_id = r.id
WHERE dl.date_cooked >= date('now', '-30 days');
```

5. **Analyze and adjust weights based on these rules:**

   - **Autoimmune score weight:** If the user's health_score_trend is "declining", increase `autoimmune_score` weight by 0.05 (to push healthier recipes). If "improving", keep it steady or decrease by 0.02 (user is already doing well).
   - **User rating history weight:** If the user's average rating is below 3.5, increase `user_rating_history` by 0.05 (lean more on what they actually liked). If above 4.0, decrease by 0.02 (they like most things, so other factors matter more).
   - **Ingredient preference weight:** If `disliked_ingredients` has more than 5 entries, increase `ingredient_preference` by 0.05 (the user is picky, so respect their preferences). Otherwise keep steady.
   - **Cuisine match weight:** If the user has clear cuisine preferences (preferred list has entries and avoided list has entries), increase `cuisine_match` by 0.05. If no clear pattern, decrease by 0.02.
   - **Cooking time fit weight:** If `prefers_quick_meals` is true and average total time for top-rated dishes is under 30 minutes, increase `cooking_time_fit` by 0.05. Otherwise keep steady.
   - **Variety bonus weight:** If adherence is below 60%, increase `variety_bonus` by 0.03 (the user might be bored, so suggest more variety). If above 80%, decrease by 0.02 (they are happy with current selections).

6. **Normalize weights** so they sum to exactly 1.0. After all adjustments, divide each weight by the total sum of all weights.

7. **Write the updated weights** to `backend/app/data/recommendation_weights.json` (create the `data/` directory if it does not exist):

```json
{
  "generated_at": "2026-03-09T12:00:00Z",
  "weights": {
    "autoimmune_score": 0.28,
    "user_rating_history": 0.25,
    "ingredient_preference": 0.22,
    "cuisine_match": 0.12,
    "cooking_time_fit": 0.08,
    "variety_bonus": 0.05
  },
  "adjustments_made": [
    "Increased ingredient_preference: user has 7 disliked ingredients",
    "Increased cuisine_match: clear cuisine preferences detected"
  ],
  "previous_weights": {
    "autoimmune_score": 0.30,
    "user_rating_history": 0.25,
    "ingredient_preference": 0.20,
    "cuisine_match": 0.10,
    "cooking_time_fit": 0.10,
    "variety_bonus": 0.05
  }
}
```

8. **Print a summary** to the console showing: each weight before and after adjustment, what adjustments were made and why, and confirmation that weights sum to 1.0.

## Notes

- All weights must remain between 0.02 and 0.50 (clamp before normalizing to prevent any single factor from dominating or becoming negligible).
- Keep the `previous_weights` field so changes can be reviewed over time.
- The `adjustments_made` array should contain human-readable strings explaining each change, so the developer can understand why weights shifted.
- If there are fewer than 5 dish logs in the last 30 days, print a warning that there is limited data and make conservative adjustments (halve all adjustment amounts).
