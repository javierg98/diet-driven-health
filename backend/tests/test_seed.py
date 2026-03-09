import json
import os

from app.services.seed import load_seed_recipes, seed_database
from app.models.recipe import Recipe


def test_seed_file_exists():
    path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "seed_recipes.json")
    assert os.path.exists(path)


def test_seed_file_has_recipes():
    path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "seed_recipes.json")
    with open(path) as f:
        recipes = json.load(f)
    assert len(recipes) >= 200
    for recipe in recipes:
        assert "name" in recipe
        assert "ingredients" in recipe
        assert "instructions" in recipe
        assert "tags" in recipe
        assert "autoimmune_score" in recipe


def test_seed_database(db):
    seed_database(db)
    count = db.query(Recipe).count()
    assert count >= 200


def test_seed_database_idempotent(db):
    seed_database(db)
    seed_database(db)
    count = db.query(Recipe).count()
    assert count >= 200  # no duplicates
