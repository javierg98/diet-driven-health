import json
import os
from unittest.mock import patch

from app.models.recipe import Recipe
from app.models.food_preference import FoodPreference
from app.services.recommender import (
    score_recipe,
    generate_meal_plan,
    DEFAULT_WEIGHTS,
)


def _seed_varied_recipes(db):
    """Seed recipes with different properties for scoring tests."""
    recipes_data = [
        {"name": "Salmon Bowl", "tags": ["anti-inflammatory", "dinner"], "autoimmune_score": 5,
         "ingredients": [{"name": "salmon", "quantity": 1, "unit": "lb"}, {"name": "rice", "quantity": 1, "unit": "cup"}],
         "prep_time_minutes": 10, "cook_time_minutes": 20, "difficulty": "intermediate"},
        {"name": "Chicken Tacos", "tags": ["dinner"], "autoimmune_score": 3,
         "ingredients": [{"name": "chicken", "quantity": 1, "unit": "lb"}, {"name": "tortilla", "quantity": 4, "unit": "piece"}],
         "prep_time_minutes": 15, "cook_time_minutes": 25, "difficulty": "intermediate"},
        {"name": "Quick Oats", "tags": ["breakfast", "anti-inflammatory"], "autoimmune_score": 4,
         "ingredients": [{"name": "oats", "quantity": 1, "unit": "cup"}, {"name": "blueberries", "quantity": 0.5, "unit": "cup"}],
         "prep_time_minutes": 5, "cook_time_minutes": 5, "difficulty": "beginner"},
        {"name": "Avocado Toast", "tags": ["breakfast"], "autoimmune_score": 3,
         "ingredients": [{"name": "bread", "quantity": 2, "unit": "slice"}, {"name": "avocado", "quantity": 1, "unit": "piece"}],
         "prep_time_minutes": 5, "cook_time_minutes": 0, "difficulty": "beginner"},
        {"name": "Rice Stir Fry", "tags": ["dinner", "anti-inflammatory"], "autoimmune_score": 4,
         "ingredients": [{"name": "rice", "quantity": 1, "unit": "cup"}, {"name": "broccoli", "quantity": 1, "unit": "cup"}],
         "prep_time_minutes": 10, "cook_time_minutes": 15, "difficulty": "intermediate"},
    ]
    for i, data in enumerate(recipes_data):
        recipe = Recipe(
            name=data["name"], description=f"Test {i}", ingredients=data["ingredients"],
            instructions=["Step 1"], prep_time_minutes=data["prep_time_minutes"],
            cook_time_minutes=data["cook_time_minutes"], difficulty=data["difficulty"],
            servings=2, tags=data["tags"], autoimmune_score=data["autoimmune_score"],
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        )
        db.add(recipe)
    db.commit()


def test_default_weights_sum_to_one():
    total = sum(DEFAULT_WEIGHTS.values())
    assert abs(total - 1.0) < 0.01


def test_score_recipe_preference_boost(db):
    _seed_varied_recipes(db)
    pref = FoodPreference(user_id=1, type="like", value="salmon", category="ingredient")
    db.add(pref)
    db.commit()

    recipes = db.query(Recipe).all()
    salmon_recipe = next(r for r in recipes if r.name == "Salmon Bowl")
    chicken_recipe = next(r for r in recipes if r.name == "Chicken Tacos")

    likes = ["salmon"]
    dislikes = []
    planned_ingredients = set()

    salmon_score = score_recipe(salmon_recipe, likes, dislikes, planned_ingredients, DEFAULT_WEIGHTS)
    chicken_score = score_recipe(chicken_recipe, likes, dislikes, planned_ingredients, DEFAULT_WEIGHTS)

    assert salmon_score > chicken_score


def test_score_recipe_dislike_penalty(db):
    _seed_varied_recipes(db)
    recipes = db.query(Recipe).all()
    chicken_recipe = next(r for r in recipes if r.name == "Chicken Tacos")

    likes = []
    dislikes = ["chicken"]
    planned_ingredients = set()

    score = score_recipe(chicken_recipe, likes, dislikes, planned_ingredients, DEFAULT_WEIGHTS)
    score_no_dislike = score_recipe(chicken_recipe, [], [], planned_ingredients, DEFAULT_WEIGHTS)

    assert score < score_no_dislike


def test_score_recipe_overlap_bonus(db):
    _seed_varied_recipes(db)
    recipes = db.query(Recipe).all()
    rice_stir_fry = next(r for r in recipes if r.name == "Rice Stir Fry")

    planned_with_rice = {"rice"}
    planned_empty = set()

    score_with = score_recipe(rice_stir_fry, [], [], planned_with_rice, DEFAULT_WEIGHTS)
    score_without = score_recipe(rice_stir_fry, [], [], planned_empty, DEFAULT_WEIGHTS)

    assert score_with > score_without


def test_generate_plan_returns_correct_structure(db):
    _seed_varied_recipes(db)
    for i in range(20):
        db.add(Recipe(
            name=f"Extra {i}", description="", ingredients=[{"name": f"item{i}", "quantity": 1, "unit": "cup"}],
            instructions=["Step 1"], difficulty="intermediate", servings=2,
            tags=[], autoimmune_score=3,
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        ))
    db.commit()

    plan = generate_meal_plan(
        db, skill_level="intermediate",
        meal_types=["breakfast", "lunch", "dinner"],
    )
    assert len(plan) == 7
    for day in plan:
        assert "breakfast" in day
        assert "lunch" in day
        assert "dinner" in day


def test_generate_plan_respects_meal_types(db):
    _seed_varied_recipes(db)
    for i in range(20):
        db.add(Recipe(
            name=f"Extra {i}", description="", ingredients=[{"name": f"item{i}", "quantity": 1, "unit": "cup"}],
            instructions=["Step 1"], difficulty="intermediate", servings=2,
            tags=[], autoimmune_score=3,
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        ))
    db.commit()

    plan = generate_meal_plan(
        db, skill_level="intermediate",
        meal_types=["lunch", "dinner"],
    )
    assert len(plan) == 7
    for day in plan:
        assert day.get("breakfast") is None
        assert day["lunch"] is not None
        assert day["dinner"] is not None


def test_generate_plan_with_cooking_session_limit(db):
    for i in range(25):
        db.add(Recipe(
            name=f"Recipe {i}", description="", ingredients=[{"name": f"item{i}", "quantity": 1, "unit": "cup"}],
            instructions=["Step 1"], difficulty="intermediate", servings=2,
            tags=[], autoimmune_score=3,
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        ))
    db.commit()

    plan = generate_meal_plan(
        db, skill_level="intermediate",
        meal_types=["breakfast", "lunch", "dinner"],
        cooking_sessions=4,
    )
    assert len(plan) == 7
