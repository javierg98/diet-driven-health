# Recipe Analyzer Skill

Analyze personal recipes to identify ingredient patterns, flavor profiles, and cuisine preferences.

## When to Use

Run this skill after the user has added several personal recipes (source="personal") to the database. It helps the recommender understand what kinds of recipes the user gravitates toward when cooking on their own.

## Instructions

1. **Connect to the database** at `backend/diet_driven_health.db` using Python and sqlite3.

2. **Query all personal recipes:**

```sql
SELECT id, name, ingredients, tags, autoimmune_score, difficulty, nutrition, prep_time_minutes, cook_time_minutes
FROM recipes
WHERE source = 'personal';
```

3. **Query food entries for detected ingredients:**

```sql
SELECT id, name, ingredients, source_type, created_at
FROM food_entries
ORDER BY created_at DESC;
```

4. **Query food preferences for explicit likes/dislikes:**

```sql
SELECT id, food_name, preference_type, notes, created_at
FROM food_preferences
ORDER BY created_at DESC;
```

5. **Parse the data.** The `ingredients`, `tags`, and `nutrition` columns are JSON strings. Parse them with `json.loads()`. Food entries and preferences provide additional signals for the taste profile analysis alongside personal recipes.

6. **Analyze the following dimensions:**

   - **Ingredient frequency:** Count how often each ingredient name appears across all personal recipes and food entries. Include ingredients detected in food entries alongside recipe ingredients. Identify the top 20 most-used ingredients.
   - **Explicit preferences:** Incorporate food preferences (likes and dislikes) into the taste profile. Liked foods should boost related ingredient counts. Disliked foods should be flagged separately as ingredients to avoid.
   - **Cuisine types:** Infer cuisine categories from tags (e.g., "mexican", "mediterranean", "asian"). Count occurrences of each.
   - **Flavor profiles:** Look for flavor-indicating ingredients and tags. Group into categories: savory, spicy, sweet, acidic/tangy, umami, herbal/fresh. Count recipes that fall into each.
   - **Cooking complexity:** Tally recipes by difficulty level ("easy", "intermediate", "advanced"). Compute average total cook time (prep_time_minutes + cook_time_minutes).
   - **Autoimmune score distribution:** Count recipes at each autoimmune_score level (1-5).
   - **Nutritional tendencies:** If nutrition data is present, compute averages for calories, protein, carbs, fat, fiber across all personal recipes.

7. **Write results** to `backend/app/data/user_preferences.json` (create the `data/` directory if it does not exist). Use the following JSON structure:

```json
{
  "generated_at": "2026-03-09T12:00:00Z",
  "total_personal_recipes": 12,
  "top_ingredients": [
    {"name": "garlic", "count": 10},
    {"name": "olive oil", "count": 8}
  ],
  "cuisine_preferences": [
    {"cuisine": "mediterranean", "count": 5},
    {"cuisine": "mexican", "count": 3}
  ],
  "flavor_profile": {
    "savory": 8,
    "spicy": 4,
    "sweet": 2,
    "acidic_tangy": 3,
    "umami": 5,
    "herbal_fresh": 6
  },
  "complexity_preferences": {
    "difficulty_distribution": {"easy": 3, "intermediate": 7, "advanced": 2},
    "avg_total_time_minutes": 45
  },
  "autoimmune_score_distribution": {"1": 0, "2": 1, "3": 4, "4": 5, "5": 2},
  "nutritional_averages": {
    "calories": 350,
    "protein_g": 25,
    "carbs_g": 40,
    "fat_g": 12,
    "fiber_g": 8
  }
}
```

8. **Print a summary** to the console showing: total recipes analyzed, top 5 ingredients, preferred cuisine, average complexity, and average autoimmune score.

## Notes

- If there are no personal recipes yet, write a minimal JSON file with `total_personal_recipes: 0` and print a message saying there is not enough data.
- Ingredient names should be normalized to lowercase and trimmed of whitespace before counting.
- The flavor profile analysis uses heuristics. Map common ingredients to profiles, e.g.: chili/jalapeno -> spicy, lemon/lime/vinegar -> acidic_tangy, soy sauce/miso -> umami, basil/cilantro/mint -> herbal_fresh, honey/maple -> sweet.
