# Recipe Validator Skill

Validate seed recipes for data quality, nutrition accuracy, and autoimmune score consistency.

## When to Use

Run after generating or modifying seed_recipes.json to catch data quality issues.

## Instructions

1. **Load the seed recipes** from `backend/app/data/seed_recipes.json`.

2. **Validate each recipe** against these rules:

   **Required fields:** name, description, ingredients (non-empty list), instructions (non-empty list), prep_time_minutes (>0), cook_time_minutes (>=0), difficulty (beginner|intermediate|advanced), servings (>0), tags (non-empty list), autoimmune_score (1-5), nutrition (all 5 fields present), source.

   **Ingredient format:** Each must have name (non-empty string), quantity (number > 0), unit (non-empty string).

   **Nutrition ranges:**
   - calories: 50-1200 per serving
   - protein: 0-80g
   - sodium: 0-1500mg
   - potassium: 0-2000mg
   - phosphorus: 0-800mg

   **Autoimmune score consistency:**
   - Score 5: Should NOT contain nightshades (tomato, pepper, potato, eggplant), dairy, or gluten
   - Score 4: At most 1 borderline ingredient
   - Score 1-2: Should contain multiple inflammatory ingredients

   **Tag consistency:**
   - "kidney-friendly" recipes should have potassium < 600mg and phosphorus < 300mg
   - "low-sodium" recipes should have sodium < 300mg
   - "gluten-free" should not contain flour, bread, pasta, wheat
   - "dairy-free" should not contain milk, cream, cheese, butter, yogurt

   **No duplicates:** No two recipes should have the same name (case-insensitive).

3. **Print results** grouped by severity:
   - ERRORS: Must fix (missing fields, out-of-range values)
   - WARNINGS: Should review (score inconsistencies, tag mismatches)
   - INFO: Statistics (total count, distribution by cuisine/meal type/score)

4. **Fix any errors** found by updating the recipe data directly.
