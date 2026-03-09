import json
import os

from sqlalchemy.orm import Session

from app.models.recipe import Recipe


def load_seed_recipes() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_recipes.json")
    with open(path) as f:
        return json.load(f)


def seed_database(db: Session) -> int:
    recipes = load_seed_recipes()
    existing_names = {r.name for r in db.query(Recipe.name).all()}
    added = 0
    for recipe_data in recipes:
        if recipe_data["name"] not in existing_names:
            recipe = Recipe(**recipe_data)
            db.add(recipe)
            added += 1
    db.commit()
    return added
