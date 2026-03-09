# Seed Recipe Overhaul — Design Document

**Date:** 2026-03-09
**Status:** Approved

## Overview

Overhaul the seed recipe database from 25 to 200+ recipes with research-backed nutrition data, AIP-based autoimmune scoring, and strong Mexican/Mediterranean representation. Leverage external recipe databases, enrich with nutrition and autoimmune data, and validate with a Claude Code skill.

## Data Sources (Priority Order)

1. **TheMealDB API** (primary) — Free, no auth, structured JSON with ingredients + instructions + cuisine categories. ~300 recipes available. No nutrition data — we enrich ourselves.
   - API: `https://www.themealdb.com/api/json/v1/1/`
   - Filter by area: Mexican, various categories (Seafood, Chicken, Beef, Vegetarian, etc.)

2. **GitHub recipe datasets** — `josephrmartinez/recipe-dataset` (13,500 recipes), `ada-food-recipes/food-recipes` (~400 with nutrition + region). Filter for Mexican and Mediterranean.

3. **AIP recipe sites** — Autoimmune Wellness (~400 AIP-compliant recipes), Wendi's AIP Kitchen. High autoimmune scores, minimal adaptation.

4. **Claude knowledge** — Fill cuisine gaps, create adaptations, ensure variety.

## Pipeline

```
1. Fetch from TheMealDB API (Mexican, Seafood, etc.)
2. Filter for relevance (skip desserts, deep-fried, etc.)
3. Transform to our Recipe schema
4. Enrich: nutrition (USDA-based), autoimmune score, tags
5. Flag adaptation level
6. Validate with skill
7. Write to seed_recipes.json
```

## Enrichment

For each recipe from external sources:
- **Nutrition:** Estimate per-serving values from ingredient composition using USDA FoodData Central knowledge (calories, protein, sodium, potassium, phosphorus)
- **Autoimmune score (1-5):**
  - 5: All AIP-compliant, anti-inflammatory spices, no triggers
  - 4: Mostly compliant, 1 borderline ingredient (eggs, rice)
  - 3: Contains reintroduction-phase foods (nightshades, dairy-free cheese)
  - 2: Multiple triggers, manageable in moderation
  - 1: Comfort food with known triggers — included for adherence
- **Tags:** Auto-assign from ingredients/cuisine (anti-inflammatory, kidney-friendly, low-sodium, gluten-free, dairy-free, etc.)
- **Adaptation flag:** `none`, `minor` (1-2 swaps), `significant` (major rework)

## Target Distribution

| Category | Count | Focus |
|----------|-------|-------|
| Breakfast | 40-50 | Quick options + weekend specials |
| Lunch | 60-70 | Salads, wraps, bowls, soups |
| Dinner | 80-90 | Main courses with sides |
| Snacks/Sides | 20-30 | Light bites, dips |

| Cuisine | ~% |
|---------|-----|
| Mexican / Latin | 30% |
| Mediterranean | 30% |
| American / comfort | 15% |
| Asian-inspired | 15% |
| Other | 10% |

## Validation Skill

A Claude Code skill (`recipe-validator`) that checks:
- Required fields present and non-empty
- Nutrition in reasonable ranges (calories 100-1200, protein 0-80g, sodium 0-1500mg, potassium 0-2000mg, phosphorus 0-800mg)
- Autoimmune score justified by ingredients (nightshade recipe != score 5)
- Tag consistency (kidney-friendly != high potassium)
- No duplicate recipe names
- Ingredient format matches schema (name, quantity, unit)

## Schema Reference

Each recipe in `seed_recipes.json`:
```json
{
  "name": "string",
  "description": "string",
  "ingredients": [{"name": "string", "quantity": number, "unit": "string"}],
  "instructions": ["string"],
  "prep_time_minutes": number,
  "cook_time_minutes": number,
  "difficulty": "beginner|intermediate|advanced",
  "servings": number,
  "tags": ["string"],
  "autoimmune_score": 1-5,
  "nutrition": {"calories": number, "protein": number, "sodium": number, "potassium": number, "phosphorus": number},
  "source": "seeded"
}
```
