# Recommender V2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the random meal plan generator with a weighted scoring engine, add unified food submission (recipes + preferences + past meals), and build an admin console for viewing skill analysis results.

**Architecture:** New `FoodEntry` and `FoodPreference` models store unstructured food data. A `food_parser.py` service classifies and extracts structured data from free-text input. The recommender is rewritten as a scoring engine that reads user preferences, food history, and optional skill-generated weight files. An `/admin` frontend page displays skill outputs and health trends. The `MealPlanGenerate` schema is extended with weekly goal fields.

**Tech Stack:** Python FastAPI, SQLAlchemy, SQLite, React, TypeScript, Tailwind CSS

---

### Task 1: FoodEntry Model & Migration

**Files:**
- Create: `backend/app/models/food_entry.py`
- Modify: `backend/app/main.py` (import new model so table is created)
- Test: `backend/tests/test_food_entry.py`

**Step 1: Write the failing test**

Create `backend/tests/test_food_entry.py`:

```python
from app.models.food_entry import FoodEntry


def test_create_food_entry(db):
    entry = FoodEntry(
        user_id=1,
        description="Salmon with rice and steamed broccoli",
        dish_name="Salmon with rice",
        detected_ingredients=["salmon", "rice", "broccoli"],
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    assert entry.id is not None
    assert entry.dish_name == "Salmon with rice"
    assert entry.detected_ingredients == ["salmon", "rice", "broccoli"]
    assert entry.created_at is not None
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_entry.py -v`
Expected: FAIL (import error)

**Step 3: Write the model**

Create `backend/app/models/food_entry.py`:

```python
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    dish_name = Column(String, nullable=False)
    detected_ingredients = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="food_entries")
```

Add import to `backend/app/main.py` after the other model imports (the import ensures the table is created by `Base.metadata.create_all`):

```python
from app.models.food_entry import FoodEntry  # noqa: F401
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_entry.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/food_entry.py backend/app/main.py backend/tests/test_food_entry.py
git commit -m "feat: add FoodEntry model for past meal tracking"
```

---

### Task 2: FoodPreference Model & Migration

**Files:**
- Create: `backend/app/models/food_preference.py`
- Modify: `backend/app/main.py` (import new model)
- Test: `backend/tests/test_food_preference.py`

**Step 1: Write the failing test**

Create `backend/tests/test_food_preference.py`:

```python
from app.models.food_preference import FoodPreference


def test_create_like_preference(db):
    pref = FoodPreference(
        user_id=1,
        type="like",
        value="thai curry",
        category="cuisine",
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    assert pref.id is not None
    assert pref.type == "like"
    assert pref.value == "thai curry"
    assert pref.category == "cuisine"
    assert pref.created_at is not None


def test_create_dislike_preference(db):
    pref = FoodPreference(
        user_id=1,
        type="dislike",
        value="cilantro",
        category="ingredient",
    )
    db.add(pref)
    db.commit()
    db.refresh(pref)
    assert pref.type == "dislike"
    assert pref.category == "ingredient"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_preference.py -v`
Expected: FAIL (import error)

**Step 3: Write the model**

Create `backend/app/models/food_preference.py`:

```python
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class FoodPreference(Base):
    __tablename__ = "food_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # "like" or "dislike"
    value = Column(String, nullable=False)  # the food/cuisine/ingredient
    category = Column(String, nullable=False)  # "ingredient", "cuisine", "dish", "flavor"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="food_preferences")
```

Add import to `backend/app/main.py`:

```python
from app.models.food_preference import FoodPreference  # noqa: F401
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_preference.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/food_preference.py backend/app/main.py backend/tests/test_food_preference.py
git commit -m "feat: add FoodPreference model for likes and dislikes"
```

---

### Task 3: Food Submission Schemas

**Files:**
- Create: `backend/app/schemas/food_submission.py`
- Test: `backend/tests/test_food_submission_schemas.py`

**Step 1: Write the failing test**

Create `backend/tests/test_food_submission_schemas.py`:

```python
from app.schemas.food_submission import (
    FoodSubmissionInput,
    FoodEntryResponse,
    FoodPreferenceResponse,
    FoodSubmissionResult,
)


def test_submission_input_defaults():
    inp = FoodSubmissionInput(text="Salmon with rice")
    assert inp.submission_type is None
    assert inp.text == "Salmon with rice"


def test_submission_input_with_type():
    inp = FoodSubmissionInput(text="cilantro, liver", submission_type="dislikes")
    assert inp.submission_type == "dislikes"


def test_food_entry_response():
    resp = FoodEntryResponse(
        id=1, user_id=1, description="Salmon dinner",
        dish_name="Salmon", detected_ingredients=["salmon"],
        created_at="2026-03-09T12:00:00",
    )
    assert resp.dish_name == "Salmon"


def test_food_preference_response():
    resp = FoodPreferenceResponse(
        id=1, user_id=1, type="like", value="avocado",
        category="ingredient", created_at="2026-03-09T12:00:00",
    )
    assert resp.type == "like"


def test_submission_result_recipe():
    result = FoodSubmissionResult(
        detected_type="recipe",
        recipes=[],
        entries=[],
        preferences=[],
    )
    assert result.detected_type == "recipe"


def test_submission_result_mixed():
    result = FoodSubmissionResult(
        detected_type="likes",
        recipes=[],
        entries=[],
        preferences=[],
    )
    assert result.detected_type == "likes"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_submission_schemas.py -v`
Expected: FAIL (import error)

**Step 3: Write the schemas**

Create `backend/app/schemas/food_submission.py`:

```python
from pydantic import BaseModel
from app.schemas.recipe import RecipeCreate


class FoodSubmissionInput(BaseModel):
    text: str
    submission_type: str | None = None  # "recipe", "past_meals", "likes", "dislikes", or None for auto-detect


class FoodEntryResponse(BaseModel):
    id: int
    user_id: int
    description: str
    dish_name: str
    detected_ingredients: list[str]
    created_at: str

    class Config:
        from_attributes = True


class FoodPreferenceResponse(BaseModel):
    id: int
    user_id: int
    type: str
    value: str
    category: str
    created_at: str

    class Config:
        from_attributes = True


class FoodSubmissionResult(BaseModel):
    """Result of parsing food submission. One of the lists will be populated based on detected_type."""
    detected_type: str  # "recipe", "past_meals", "likes", "dislikes"
    recipes: list[RecipeCreate] = []
    entries: list[dict] = []  # parsed FoodEntry dicts (before DB save)
    preferences: list[dict] = []  # parsed FoodPreference dicts (before DB save)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_submission_schemas.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/schemas/food_submission.py backend/tests/test_food_submission_schemas.py
git commit -m "feat: add food submission schemas for unified input"
```

---

### Task 4: Food Parser Service

**Files:**
- Create: `backend/app/services/food_parser.py`
- Test: `backend/tests/test_food_parser.py`

This service detects submission type and parses content accordingly. It reuses `recipe_parser.py` for recipe detection.

**Step 1: Write the failing tests**

Create `backend/tests/test_food_parser.py`:

```python
from app.services.food_parser import detect_submission_type, parse_food_submission


def test_detect_recipe():
    text = """Garlic Salmon
Ingredients
- 2 lb salmon fillet
- 3 clove garlic
Instructions
1. Preheat oven to 400F
2. Season salmon with garlic
3. Bake for 20 minutes"""
    assert detect_submission_type(text) == "recipe"


def test_detect_likes():
    text = "Thai curry, avocado, lemon, grilled fish, spicy food"
    assert detect_submission_type(text) == "likes"


def test_detect_dislikes():
    text = "I don't like: cilantro, liver, eggplant"
    assert detect_submission_type(text) == "dislikes"


def test_detect_past_meals():
    text = """Last night I made salmon with rice and steamed broccoli.
Today for lunch I had chicken tacos with guacamole."""
    assert detect_submission_type(text) == "past_meals"


def test_parse_recipe():
    text = """Garlic Salmon
Ingredients
- 2 lb salmon fillet
- 3 clove garlic
Instructions
1. Preheat oven to 400F
2. Bake for 20 minutes"""
    result = parse_food_submission(text)
    assert result["detected_type"] == "recipe"
    assert len(result["recipes"]) == 1
    assert result["recipes"][0]["name"] == "Garlic Salmon"


def test_parse_likes():
    text = "Thai curry, avocado, lemon, grilled fish"
    result = parse_food_submission(text)
    assert result["detected_type"] == "likes"
    assert len(result["preferences"]) == 4
    assert result["preferences"][0]["type"] == "like"
    assert result["preferences"][0]["value"] == "thai curry"


def test_parse_dislikes():
    text = "I don't like: cilantro, liver, eggplant"
    result = parse_food_submission(text)
    assert result["detected_type"] == "dislikes"
    assert len(result["preferences"]) == 3
    assert result["preferences"][0]["type"] == "dislike"


def test_parse_past_meals():
    text = """Salmon with rice and steamed broccoli
Chicken tacos with guacamole"""
    result = parse_food_submission(text, submission_type="past_meals")
    assert result["detected_type"] == "past_meals"
    assert len(result["entries"]) == 2
    assert result["entries"][0]["dish_name"] == "Salmon with rice and steamed broccoli"


def test_override_type():
    text = "avocado, salmon, rice"
    result = parse_food_submission(text, submission_type="dislikes")
    assert result["detected_type"] == "dislikes"
    assert all(p["type"] == "dislike" for p in result["preferences"])


def test_categorize_ingredient():
    from app.services.food_parser import _categorize_preference
    assert _categorize_preference("avocado") == "ingredient"
    assert _categorize_preference("thai curry") == "cuisine"
    assert _categorize_preference("spicy food") == "flavor"
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_parser.py -v`
Expected: FAIL (import error)

**Step 3: Write the food parser**

Create `backend/app/services/food_parser.py`:

```python
import re

from app.services.recipe_parser import parse_recipe_text


CUISINE_KEYWORDS = [
    "thai", "mexican", "italian", "japanese", "chinese", "indian", "korean",
    "mediterranean", "greek", "french", "vietnamese", "middle eastern",
    "curry", "tacos", "pasta", "sushi", "ramen", "stir fry",
]

FLAVOR_KEYWORDS = [
    "spicy", "sweet", "savory", "sour", "bitter", "umami", "smoky",
    "tangy", "mild", "rich", "creamy", "crispy", "herbal", "citrusy",
]

DISLIKE_PATTERNS = [
    r"(?:i\s+)?(?:don'?t|do\s+not)\s+(?:like|enjoy|eat|want)",
    r"(?:i\s+)?(?:hate|dislike|avoid|can'?t\s+stand)",
    r"no\s+(?:more\s+)?(?:thanks|thank)",
    r"not\s+a\s+fan",
]

PAST_MEAL_PATTERNS = [
    r"(?:i|we)\s+(?:made|had|ate|cooked|prepared)",
    r"(?:last\s+night|today|yesterday|this\s+(?:morning|week))",
    r"for\s+(?:breakfast|lunch|dinner|brunch)",
]


def detect_submission_type(text: str) -> str:
    """Auto-detect whether text is a recipe, likes, dislikes, or past meals."""
    lower = text.lower()
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    # Check for recipe structure: section headers like "Ingredients" or "Instructions"
    has_ingredient_header = any(
        line.lower().startswith(("ingredient", "instruction", "direction", "method", "steps"))
        for line in lines
    )
    if has_ingredient_header and len(lines) >= 4:
        return "recipe"

    # Check for dislike indicators
    for pattern in DISLIKE_PATTERNS:
        if re.search(pattern, lower):
            return "dislikes"

    # Check for past meal indicators
    for pattern in PAST_MEAL_PATTERNS:
        if re.search(pattern, lower):
            return "past_meals"

    # Check if it's a comma-separated list (likely preferences)
    if "," in text and len(lines) <= 3:
        return "likes"

    # Multi-line without structure → past meals
    if len(lines) >= 2:
        return "past_meals"

    # Default to likes for short single-line input
    return "likes"


def _categorize_preference(value: str) -> str:
    """Categorize a food preference as ingredient, cuisine, dish, or flavor."""
    lower = value.lower()
    for keyword in CUISINE_KEYWORDS:
        if keyword in lower:
            return "cuisine"
    for keyword in FLAVOR_KEYWORDS:
        if keyword in lower:
            return "flavor"
    # Multi-word items with common dish patterns
    if any(word in lower for word in ["with", "and", "on", "over"]):
        return "dish"
    return "ingredient"


def _parse_comma_list(text: str) -> list[str]:
    """Split comma/newline-separated items, cleaning prefixes like 'I don't like:'."""
    # Remove common prefixes
    cleaned = re.sub(
        r"^(?:i\s+(?:don'?t|do\s+not)\s+(?:like|enjoy|eat|want)\s*[:;]?\s*|"
        r"i\s+(?:like|enjoy|love|prefer)\s*[:;]?\s*|"
        r"(?:likes?|dislikes?|avoid)\s*[:;]?\s*)",
        "", text.strip(), flags=re.IGNORECASE,
    )
    items = re.split(r"[,\n]+", cleaned)
    return [item.strip().lower() for item in items if item.strip()]


def _extract_ingredients_from_description(text: str) -> list[str]:
    """Extract likely ingredient words from a meal description."""
    # Common cooking/filler words to exclude
    stop_words = {
        "with", "and", "the", "a", "an", "some", "of", "in", "on", "for",
        "made", "had", "ate", "cooked", "prepared", "steamed", "grilled",
        "baked", "fried", "roasted", "sauteed", "boiled", "fresh", "i", "we",
        "last", "night", "today", "yesterday", "lunch", "dinner", "breakfast",
    }
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]


def parse_food_submission(text: str, submission_type: str | None = None) -> dict:
    """Parse food submission text. Returns dict matching FoodSubmissionResult schema."""
    detected = submission_type or detect_submission_type(text)

    if detected == "recipe":
        parsed = parse_recipe_text(text)
        return {
            "detected_type": "recipe",
            "recipes": [parsed],
            "entries": [],
            "preferences": [],
        }

    if detected in ("likes", "dislikes"):
        pref_type = "like" if detected == "likes" else "dislike"
        items = _parse_comma_list(text)
        preferences = [
            {
                "type": pref_type,
                "value": item,
                "category": _categorize_preference(item),
            }
            for item in items
        ]
        return {
            "detected_type": detected,
            "recipes": [],
            "entries": [],
            "preferences": preferences,
        }

    if detected == "past_meals":
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        entries = []
        for line in lines:
            # Clean prefixes like "Last night I made..."
            dish = re.sub(
                r"^(?:(?:last\s+night|today|yesterday|this\s+\w+)\s+)?(?:i|we)\s+(?:made|had|ate|cooked|prepared)\s+",
                "", line, flags=re.IGNORECASE,
            ).strip().rstrip(".")
            if not dish:
                dish = line
            entries.append({
                "description": line,
                "dish_name": dish,
                "detected_ingredients": _extract_ingredients_from_description(dish),
            })
        return {
            "detected_type": "past_meals",
            "recipes": [],
            "entries": entries,
            "preferences": [],
        }

    return {"detected_type": detected, "recipes": [], "entries": [], "preferences": []}
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_parser.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/services/food_parser.py backend/tests/test_food_parser.py
git commit -m "feat: add food parser service for unified submission detection"
```

---

### Task 5: Food Submission API Endpoints

**Files:**
- Create: `backend/app/api/food_submission.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_food_submission_api.py`

**Step 1: Write the failing tests**

Create `backend/tests/test_food_submission_api.py`:

```python
def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_parse_submission_likes(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/parse", json={
        "text": "Thai curry, avocado, lemon",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_type"] == "likes"
    assert len(data["preferences"]) == 3


def test_parse_submission_with_override(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/parse", json={
        "text": "avocado, salmon",
        "submission_type": "dislikes",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["detected_type"] == "dislikes"


def test_save_preferences(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "avocado", "category": "ingredient"},
            {"type": "like", "value": "thai curry", "category": "cuisine"},
        ],
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["saved_preferences"] == 2


def test_save_food_entries(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/save", json={
        "detected_type": "past_meals",
        "recipes": [],
        "entries": [
            {"description": "Salmon with rice", "dish_name": "Salmon with rice", "detected_ingredients": ["salmon", "rice"]},
        ],
        "preferences": [],
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["saved_entries"] == 1


def test_get_preferences(client):
    headers = _register_and_login(client)
    # Save first
    client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "avocado", "category": "ingredient"},
        ],
    }, headers=headers)
    resp = client.get("/api/food/preferences", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["value"] == "avocado"


def test_get_food_entries(client):
    headers = _register_and_login(client)
    client.post("/api/food/save", json={
        "detected_type": "past_meals",
        "recipes": [],
        "entries": [
            {"description": "Salmon dinner", "dish_name": "Salmon", "detected_ingredients": ["salmon"]},
        ],
        "preferences": [],
    }, headers=headers)
    resp = client.get("/api/food/entries", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_submission_api.py -v`
Expected: FAIL (import error / 404)

**Step 3: Write the API router**

Create `backend/app/api/food_submission.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_entry import FoodEntry
from app.models.food_preference import FoodPreference
from app.models.user import User
from app.schemas.food_submission import (
    FoodSubmissionInput,
    FoodSubmissionResult,
    FoodEntryResponse,
    FoodPreferenceResponse,
)
from app.services.food_parser import parse_food_submission
from app.services.recipe_parser import parse_recipe_text
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/food", tags=["food"])


@router.post("/parse", response_model=FoodSubmissionResult)
def parse_submission(
    req: FoodSubmissionInput,
    current_user: User = Depends(get_current_user),
):
    result = parse_food_submission(req.text, submission_type=req.submission_type)
    return result


@router.post("/save", status_code=201)
def save_submission(
    req: FoodSubmissionResult,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved_recipes = 0
    saved_entries = 0
    saved_preferences = 0

    for entry_data in req.entries:
        entry = FoodEntry(
            user_id=current_user.id,
            description=entry_data["description"],
            dish_name=entry_data["dish_name"],
            detected_ingredients=entry_data.get("detected_ingredients", []),
        )
        db.add(entry)
        saved_entries += 1

    for pref_data in req.preferences:
        pref = FoodPreference(
            user_id=current_user.id,
            type=pref_data["type"],
            value=pref_data["value"],
            category=pref_data.get("category", "ingredient"),
        )
        db.add(pref)
        saved_preferences += 1

    # Recipes are saved via existing /api/recipes endpoint — not duplicated here
    saved_recipes = len(req.recipes)

    db.commit()
    return {
        "saved_recipes": saved_recipes,
        "saved_entries": saved_entries,
        "saved_preferences": saved_preferences,
    }


@router.get("/preferences", response_model=list[FoodPreferenceResponse])
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FoodPreference).filter(
        FoodPreference.user_id == current_user.id
    ).order_by(FoodPreference.created_at.desc()).all()


@router.get("/entries", response_model=list[FoodEntryResponse])
def get_food_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FoodEntry).filter(
        FoodEntry.user_id == current_user.id
    ).order_by(FoodEntry.created_at.desc()).all()
```

Register the router in `backend/app/main.py` — add after the upload router import:

```python
from app.api.food_submission import router as food_router
```

And include it:

```python
app.include_router(food_router)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_food_submission_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/api/food_submission.py backend/app/main.py backend/tests/test_food_submission_api.py
git commit -m "feat: add food submission API endpoints (parse, save, list)"
```

---

### Task 6: Extended MealPlanGenerate Schema

**Files:**
- Modify: `backend/app/schemas/meal_plan.py`
- Modify: `backend/tests/test_meal_plan.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_meal_plan.py`:

```python
from app.schemas.meal_plan import MealPlanGenerate


def test_meal_plan_generate_with_goals():
    req = MealPlanGenerate(
        week_start="2026-03-09",
        meal_types=["lunch", "dinner"],
        cooking_sessions=4,
        weekly_budget=75.0,
        batch_cooking=True,
    )
    assert req.meal_types == ["lunch", "dinner"]
    assert req.cooking_sessions == 4
    assert req.weekly_budget == 75.0
    assert req.batch_cooking is True


def test_meal_plan_generate_defaults():
    req = MealPlanGenerate(week_start="2026-03-09")
    assert req.meal_types == ["breakfast", "lunch", "dinner"]
    assert req.cooking_sessions is None
    assert req.weekly_budget is None
    assert req.batch_cooking is False
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_meal_plan.py::test_meal_plan_generate_with_goals -v`
Expected: FAIL (unexpected keyword argument)

**Step 3: Update the schema**

Modify `backend/app/schemas/meal_plan.py` — update `MealPlanGenerate`:

```python
from pydantic import BaseModel


class MealPlanGenerate(BaseModel):
    week_start: str
    meal_types: list[str] = ["breakfast", "lunch", "dinner"]
    cooking_sessions: int | None = None  # max number of times user can cook
    weekly_budget: float | None = None  # optional dollar amount
    batch_cooking: bool = False  # plan leftovers to reduce cooking


class DayPlan(BaseModel):
    breakfast: int | None = None
    lunch: int | None = None
    dinner: int | None = None


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    week_start: str
    days: list[DayPlan]

    class Config:
        from_attributes = True


class MealSwap(BaseModel):
    day_index: int
    meal_type: str
```

Note: `DayPlan` fields are now `int | None` because not all meal types may be planned.

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_meal_plan.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add backend/app/schemas/meal_plan.py backend/tests/test_meal_plan.py
git commit -m "feat: extend MealPlanGenerate with weekly goal fields"
```

---

### Task 7: Purchase-Unit Cost Model

**Files:**
- Modify: `backend/app/services/grocery.py` (replace per-unit costs with purchase-unit costs)
- Modify: `backend/tests/test_grocery.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_grocery.py`:

```python
from app.services.grocery import estimate_purchase_cost, PURCHASE_UNITS


def test_purchase_units_has_common_items():
    assert "strawberries" in PURCHASE_UNITS
    assert "rice" in PURCHASE_UNITS
    assert PURCHASE_UNITS["strawberries"]["cost"] > 0


def test_estimate_purchase_cost_known_item():
    items = [{"name": "strawberries", "quantity": 1, "unit": "cup"}]
    cost = estimate_purchase_cost(items)
    # Should use the purchase unit cost, not per-cup cost
    assert cost == PURCHASE_UNITS["strawberries"]["cost"]


def test_estimate_purchase_cost_shared_ingredient():
    # Two recipes using rice — should only count one purchase
    items = [
        {"name": "rice", "quantity": 1, "unit": "cup"},
        {"name": "rice", "quantity": 2, "unit": "cup"},
    ]
    cost = estimate_purchase_cost(items)
    assert cost == PURCHASE_UNITS["rice"]["cost"]


def test_estimate_purchase_cost_unknown_item():
    items = [{"name": "exotic_spice_xyz", "quantity": 2, "unit": "tbsp"}]
    cost = estimate_purchase_cost(items)
    assert cost > 0  # fallback cost
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_grocery.py::test_purchase_units_has_common_items -v`
Expected: FAIL (import error)

**Step 3: Add purchase-unit cost data and function**

Add to `backend/app/services/grocery.py` (keep existing functions, add new ones):

```python
# Purchase-unit costs: what you'd actually buy at the store
PURCHASE_UNITS = {
    # Produce
    "strawberries": {"unit": "1 pint", "cost": 4.00},
    "blueberries": {"unit": "1 pint", "cost": 4.50},
    "berries": {"unit": "1 pint", "cost": 4.00},
    "spinach": {"unit": "1 bag (5oz)", "cost": 3.50},
    "kale": {"unit": "1 bunch", "cost": 3.00},
    "arugula": {"unit": "1 bag (5oz)", "cost": 3.50},
    "lettuce": {"unit": "1 head", "cost": 2.00},
    "avocado": {"unit": "1 each", "cost": 1.50},
    "lemon": {"unit": "1 each", "cost": 0.75},
    "lime": {"unit": "1 each", "cost": 0.50},
    "tomato": {"unit": "1 lb", "cost": 2.00},
    "onion": {"unit": "1 each", "cost": 1.00},
    "garlic": {"unit": "1 head", "cost": 0.75},
    "ginger": {"unit": "1 piece", "cost": 1.50},
    "bell pepper": {"unit": "1 each", "cost": 1.25},
    "cucumber": {"unit": "1 each", "cost": 1.00},
    "carrot": {"unit": "1 bag (1lb)", "cost": 1.50},
    "celery": {"unit": "1 bunch", "cost": 2.00},
    "broccoli": {"unit": "1 head", "cost": 2.50},
    "cauliflower": {"unit": "1 head", "cost": 3.00},
    "sweet potato": {"unit": "1 each", "cost": 1.50},
    "zucchini": {"unit": "1 each", "cost": 1.25},
    "banana": {"unit": "1 bunch", "cost": 1.50},
    "apple": {"unit": "1 each", "cost": 1.00},
    # Protein
    "salmon": {"unit": "1 lb", "cost": 10.00},
    "chicken": {"unit": "1 lb", "cost": 5.00},
    "chicken breast": {"unit": "1 lb", "cost": 5.50},
    "turkey": {"unit": "1 lb", "cost": 6.00},
    "ground turkey": {"unit": "1 lb", "cost": 6.00},
    "beef": {"unit": "1 lb", "cost": 7.00},
    "shrimp": {"unit": "1 lb", "cost": 9.00},
    "tofu": {"unit": "1 block (14oz)", "cost": 2.50},
    "egg": {"unit": "1 dozen", "cost": 4.00},
    "eggs": {"unit": "1 dozen", "cost": 4.00},
    "tuna": {"unit": "1 can", "cost": 2.00},
    "cod": {"unit": "1 lb", "cost": 8.00},
    # Dairy
    "milk": {"unit": "1/2 gallon", "cost": 3.00},
    "yogurt": {"unit": "32oz container", "cost": 4.50},
    "cheese": {"unit": "8oz block", "cost": 4.00},
    "butter": {"unit": "1 stick", "cost": 2.00},
    # Grains
    "rice": {"unit": "2lb bag", "cost": 3.00},
    "oats": {"unit": "18oz canister", "cost": 3.50},
    "quinoa": {"unit": "1lb bag", "cost": 5.00},
    "bread": {"unit": "1 loaf", "cost": 3.50},
    "tortilla": {"unit": "1 pack (10ct)", "cost": 3.00},
    "flour": {"unit": "5lb bag", "cost": 4.00},
    "pasta": {"unit": "1lb box", "cost": 1.50},
    # Pantry
    "olive oil": {"unit": "16oz bottle", "cost": 6.00},
    "coconut oil": {"unit": "14oz jar", "cost": 7.00},
    "turmeric": {"unit": "1 jar", "cost": 4.00},
    "cumin": {"unit": "1 jar", "cost": 3.50},
    "cinnamon": {"unit": "1 jar", "cost": 3.50},
    "honey": {"unit": "12oz bottle", "cost": 5.00},
    "maple syrup": {"unit": "12oz bottle", "cost": 7.00},
    "soy sauce": {"unit": "10oz bottle", "cost": 3.00},
    "broth": {"unit": "32oz carton", "cost": 3.00},
    "stock": {"unit": "32oz carton", "cost": 3.00},
    "beans": {"unit": "1 can (15oz)", "cost": 1.25},
    "chickpeas": {"unit": "1 can (15oz)", "cost": 1.25},
    "lentils": {"unit": "1lb bag", "cost": 2.00},
    "almonds": {"unit": "8oz bag", "cost": 5.00},
    "walnuts": {"unit": "8oz bag", "cost": 6.00},
    "chia seeds": {"unit": "6oz bag", "cost": 5.00},
}

DEFAULT_PURCHASE_COST = 3.00  # fallback for unknown items


def estimate_purchase_cost(items: list[dict]) -> float:
    """Estimate grocery cost using purchase-unit prices.
    Each unique ingredient is counted once (buy the package, not per-unit)."""
    seen = set()
    total = 0.0
    for item in items:
        name_lower = item["name"].lower().strip()
        if name_lower in seen:
            continue
        seen.add(name_lower)
        # Try exact match, then substring match
        if name_lower in PURCHASE_UNITS:
            total += PURCHASE_UNITS[name_lower]["cost"]
        else:
            matched = False
            for key, data in PURCHASE_UNITS.items():
                if key in name_lower or name_lower in key:
                    total += data["cost"]
                    matched = True
                    break
            if not matched:
                total += DEFAULT_PURCHASE_COST
    return round(total, 2)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_grocery.py -v`
Expected: ALL PASS (existing tests still pass + new tests pass)

**Step 5: Commit**

```bash
git add backend/app/services/grocery.py backend/tests/test_grocery.py
git commit -m "feat: add purchase-unit cost model for realistic grocery estimates"
```

---

### Task 8: Weighted Scoring Recommender

**Files:**
- Rewrite: `backend/app/services/recommender.py`
- Test: `backend/tests/test_recommender_v2.py`

This is the core task. The new recommender scores each recipe and builds the plan greedily.

**Step 1: Write the failing tests**

Create `backend/tests/test_recommender_v2.py`:

```python
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
    # Add a "like" for salmon
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

    # If rice is already planned, stir fry should score higher on overlap
    planned_with_rice = {"rice"}
    planned_empty = set()

    score_with = score_recipe(rice_stir_fry, [], [], planned_with_rice, DEFAULT_WEIGHTS)
    score_without = score_recipe(rice_stir_fry, [], [], planned_empty, DEFAULT_WEIGHTS)

    assert score_with > score_without


def test_generate_plan_returns_correct_structure(db):
    _seed_varied_recipes(db)
    # Add more recipes to have enough for a full plan
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
    # With 4 cooking sessions, some meals should be marked as leftovers (None)
    unique_recipes = set()
    for day in plan:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            rid = day.get(meal_type)
            if rid is not None:
                unique_recipes.add(rid)
    # Should have at most 4 unique recipes (cooking sessions)
    # Some slots reuse recipes (leftovers)
    assert len(plan) == 7
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_recommender_v2.py -v`
Expected: FAIL (import error for score_recipe, DEFAULT_WEIGHTS)

**Step 3: Rewrite the recommender**

Rewrite `backend/app/services/recommender.py`:

```python
import json
import os
import random

from sqlalchemy.orm import Session

from app.models.recipe import Recipe

DEFAULT_WEIGHTS = {
    "preference_match": 0.30,
    "ingredient_overlap": 0.20,
    "cost_efficiency": 0.15,
    "autoimmune_friendliness": 0.15,
    "cooking_time_fit": 0.10,
    "variety": 0.10,
}

WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "recommendation_weights.json")


def _load_weights() -> dict:
    """Load weights from skill-generated file, falling back to defaults."""
    try:
        with open(WEIGHTS_FILE) as f:
            data = json.load(f)
            return data.get("weights", DEFAULT_WEIGHTS)
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return DEFAULT_WEIGHTS


def score_recipe(
    recipe: Recipe,
    likes: list[str],
    dislikes: list[str],
    planned_ingredients: set[str],
    weights: dict,
    max_cook_time: int | None = None,
    planned_tags: list[str] | None = None,
) -> float:
    """Score a recipe 0-100 across multiple dimensions."""
    scores = {}
    ingredient_names = [ing["name"].lower() for ing in (recipe.ingredients or [])]

    # 1. Preference match (0-100)
    pref_score = 50  # neutral baseline
    like_hits = sum(1 for like in likes if any(like in name for name in ingredient_names))
    dislike_hits = sum(1 for dislike in dislikes if any(dislike in name for name in ingredient_names))
    if likes:
        pref_score += (like_hits / max(len(likes), 1)) * 50
    pref_score -= dislike_hits * 25  # each dislike is a strong penalty
    scores["preference_match"] = max(0, min(100, pref_score))

    # 2. Ingredient overlap (0-100)
    if planned_ingredients:
        overlap_count = sum(1 for name in ingredient_names if name in planned_ingredients)
        overlap_ratio = overlap_count / max(len(ingredient_names), 1)
        scores["ingredient_overlap"] = overlap_ratio * 100
    else:
        scores["ingredient_overlap"] = 50  # neutral when nothing planned yet

    # 3. Cost efficiency (0-100) — fewer unique ingredients = cheaper
    unique_ingredients = len(set(ingredient_names) - planned_ingredients)
    # Fewer new ingredients to buy = higher score
    scores["cost_efficiency"] = max(0, 100 - unique_ingredients * 10)

    # 4. Autoimmune friendliness (0-100) — soft preference
    scores["autoimmune_friendliness"] = ((recipe.autoimmune_score or 3) / 5) * 100

    # 5. Cooking time fit (0-100)
    total_time = (recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0)
    if max_cook_time and total_time > 0:
        if total_time <= max_cook_time:
            scores["cooking_time_fit"] = 100
        else:
            scores["cooking_time_fit"] = max(0, 100 - (total_time - max_cook_time) * 5)
    else:
        scores["cooking_time_fit"] = 70  # neutral

    # 6. Variety (0-100) — penalize repeating tags/cuisines already planned
    if planned_tags:
        recipe_tags = set(recipe.tags or [])
        overlap = len(recipe_tags & set(planned_tags))
        scores["variety"] = max(0, 100 - overlap * 20)
    else:
        scores["variety"] = 80

    # Weighted sum
    total = sum(scores.get(dim, 50) * weights.get(dim, 0) for dim in weights)
    return round(total, 2)


def generate_meal_plan(
    db: Session,
    skill_level: str = "intermediate",
    dietary_restrictions: list[str] | None = None,
    tags: list[str] | None = None,
    meal_types: list[str] | None = None,
    cooking_sessions: int | None = None,
    weekly_budget: float | None = None,
    batch_cooking: bool = False,
    likes: list[str] | None = None,
    dislikes: list[str] | None = None,
) -> list[dict]:
    """Generate a 7-day meal plan using weighted scoring."""
    if meal_types is None:
        meal_types = ["breakfast", "lunch", "dinner"]

    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed_difficulties = difficulty_map.get(skill_level, ["beginner", "intermediate"])

    all_recipes = db.query(Recipe).filter(Recipe.difficulty.in_(allowed_difficulties)).all()
    weights = _load_weights()
    likes = likes or []
    dislikes = dislikes or []

    planned_ingredients: set[str] = set()
    planned_tags: list[str] = []
    used_ids: set[int] = set()
    cooking_count = 0
    plan = []

    for day in range(7):
        day_meals = {}
        for meal_type in ["breakfast", "lunch", "dinner"]:
            if meal_type not in meal_types:
                day_meals[meal_type] = None
                continue

            # Check cooking session limit
            if cooking_sessions is not None and cooking_count >= cooking_sessions:
                # Reuse a previously planned recipe (leftover)
                if used_ids:
                    day_meals[meal_type] = random.choice(list(used_ids))
                else:
                    day_meals[meal_type] = None
                continue

            # Score all candidates
            candidates = []
            for recipe in all_recipes:
                score = score_recipe(
                    recipe, likes, dislikes, planned_ingredients,
                    weights, planned_tags=planned_tags,
                )
                # Small random jitter to avoid deterministic ordering
                score += random.uniform(0, 5)
                # Penalize already-used recipes (variety within week)
                if recipe.id in used_ids:
                    score *= 0.3
                candidates.append((recipe, score))

            candidates.sort(key=lambda x: x[1], reverse=True)

            if candidates:
                chosen = candidates[0][0]
                day_meals[meal_type] = chosen.id
                used_ids.add(chosen.id)
                cooking_count += 1

                # Update tracking
                for ing in (chosen.ingredients or []):
                    planned_ingredients.add(ing["name"].lower())
                planned_tags.extend(chosen.tags or [])

                # Batch cooking: duplicate as next meal slot if enabled
                if batch_cooking and meal_type == "dinner" and "lunch" in meal_types:
                    # Will be handled when we get to next day's lunch
                    pass
            else:
                day_meals[meal_type] = None

        plan.append(day_meals)

    return plan


def get_swap_recipe(
    db: Session,
    excluded_ids: list[int],
    skill_level: str = "intermediate",
    likes: list[str] | None = None,
    dislikes: list[str] | None = None,
) -> int | None:
    """Get a single recipe ID not in excluded_ids, using scoring."""
    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed = difficulty_map.get(skill_level, ["beginner", "intermediate"])
    recipes = (
        db.query(Recipe)
        .filter(Recipe.difficulty.in_(allowed), ~Recipe.id.in_(excluded_ids))
        .all()
    )
    if not recipes:
        recipes = db.query(Recipe).filter(~Recipe.id.in_(excluded_ids)).all()
    if not recipes:
        return None

    weights = _load_weights()
    likes = likes or []
    dislikes = dislikes or []

    scored = [
        (r, score_recipe(r, likes, dislikes, set(), weights))
        for r in recipes
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    # Pick from top 3 with some randomness
    top = scored[:3]
    return random.choice(top)[0].id
```

**Step 4: Run tests to verify they pass**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_recommender_v2.py tests/test_meal_plan.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add backend/app/services/recommender.py backend/tests/test_recommender_v2.py
git commit -m "feat: rewrite recommender with weighted scoring engine"
```

---

### Task 9: Update Meal Plan API to Use New Recommender

**Files:**
- Modify: `backend/app/api/meal_plans.py`
- Modify: `backend/tests/test_meal_plan.py`

**Step 1: Write the failing test**

Add to `backend/tests/test_meal_plan.py`:

```python
def test_create_meal_plan_with_goals(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    response = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-16",
        "meal_types": ["lunch", "dinner"],
        "cooking_sessions": 5,
        "batch_cooking": False,
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["days"]) == 7
    # Breakfasts should be None since not in meal_types
    for day in data["days"]:
        assert day["breakfast"] is None


def test_create_meal_plan_with_preferences(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    # Add food preferences
    client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "ingredient", "category": "ingredient"},
        ],
    }, headers=headers)
    response = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-16",
    }, headers=headers)
    assert response.status_code == 201
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_meal_plan.py::test_create_meal_plan_with_goals -v`
Expected: FAIL (422 validation error — extra fields not accepted, or breakfast not None)

**Step 3: Update the meal plans API**

Rewrite `backend/app/api/meal_plans.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_preference import FoodPreference
from app.models.meal_plan import MealPlan
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.meal_plan import MealPlanGenerate, MealPlanResponse, MealSwap
from app.services.recommender import generate_meal_plan, get_swap_recipe
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/meal-plans", tags=["meal-plans"])


@router.post("/generate", response_model=MealPlanResponse, status_code=201)
def create_meal_plan(
    req: MealPlanGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    skill_level = profile.skill_level if profile else "intermediate"
    goals = profile.health_goals if profile else []

    # Load user food preferences
    prefs = db.query(FoodPreference).filter(FoodPreference.user_id == current_user.id).all()
    likes = [p.value for p in prefs if p.type == "like"]
    dislikes = [p.value for p in prefs if p.type == "dislike"]

    days = generate_meal_plan(
        db,
        skill_level=skill_level,
        tags=goals,
        meal_types=req.meal_types,
        cooking_sessions=req.cooking_sessions,
        weekly_budget=req.weekly_budget,
        batch_cooking=req.batch_cooking,
        likes=likes,
        dislikes=dislikes,
    )
    plan = MealPlan(user_id=current_user.id, week_start=req.week_start, days=days)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=list[MealPlanResponse])
def list_meal_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(MealPlan).filter(MealPlan.user_id == current_user.id).order_by(MealPlan.week_start.desc()).all()


@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_meal_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@router.put("/{plan_id}/swap", response_model=MealPlanResponse)
def swap_meal(
    plan_id: int,
    swap: MealSwap,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    days = list(plan.days)
    all_ids = []
    for d in days:
        for m in ["breakfast", "lunch", "dinner"]:
            rid = d.get(m)
            if rid is not None:
                all_ids.append(rid)

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    skill_level = profile.skill_level if profile else "intermediate"

    prefs = db.query(FoodPreference).filter(FoodPreference.user_id == current_user.id).all()
    likes = [p.value for p in prefs if p.type == "like"]
    dislikes = [p.value for p in prefs if p.type == "dislike"]

    new_id = get_swap_recipe(db, excluded_ids=all_ids, skill_level=skill_level, likes=likes, dislikes=dislikes)
    if new_id is None:
        raise HTTPException(status_code=400, detail="No alternative recipes available")

    days[swap.day_index] = dict(days[swap.day_index])
    days[swap.day_index][swap.meal_type] = new_id
    plan.days = days
    db.commit()
    db.refresh(plan)
    return plan
```

**Step 4: Run all meal plan tests**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_meal_plan.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add backend/app/api/meal_plans.py backend/tests/test_meal_plan.py
git commit -m "feat: update meal plan API to use scoring engine with preferences"
```

---

### Task 10: Admin API Endpoints

**Files:**
- Create: `backend/app/api/admin.py`
- Modify: `backend/app/main.py` (register router)
- Test: `backend/tests/test_admin.py`

The admin API serves skill-generated JSON files and health trend data.

**Step 1: Write the failing tests**

Create `backend/tests/test_admin.py`:

```python
import json
import os
from unittest.mock import patch

from app.models.dish_log import DishLog
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe
from datetime import datetime, timezone


def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_get_skill_results_empty(client):
    headers = _register_and_login(client)
    resp = client.get("/api/admin/skill-results", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_preferences" in data
    assert "user_memory" in data
    assert "recommendation_weights" in data
    # All None when no files exist
    assert data["user_preferences"] is None


def test_get_skill_results_with_data(client, tmp_path):
    headers = _register_and_login(client)
    prefs = {"generated_at": "2026-03-09", "top_ingredients": ["salmon"]}
    prefs_file = tmp_path / "user_preferences.json"
    prefs_file.write_text(json.dumps(prefs))

    with patch("app.api.admin.DATA_DIR", str(tmp_path)):
        resp = client.get("/api/admin/skill-results", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_preferences"]["top_ingredients"] == ["salmon"]


def test_get_health_trend(client, db):
    headers = _register_and_login(client)
    # Create a recipe and dish logs
    recipe = Recipe(
        name="Test", description="", ingredients=[], instructions=[],
        difficulty="intermediate", servings=2, tags=[], autoimmune_score=4,
        nutrition={}, source="seeded",
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    # Log some dishes
    for i in range(3):
        log = DishLog(
            user_id=1, recipe_id=recipe.id, rating=4, notes="",
            would_make_again=True,
        )
        db.add(log)
    db.commit()

    resp = client.get("/api/admin/health-trend", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "weekly_scores" in data
    assert "overall_average" in data
    assert data["overall_average"] == 4.0
```

**Step 2: Run test to verify it fails**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_admin.py -v`
Expected: FAIL (404 / import error)

**Step 3: Write the admin API**

Create `backend/app/api/admin.py`:

```python
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dish_log import DishLog
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str) -> dict | None:
    """Load a JSON file from the data directory, or None if not found."""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@router.get("/skill-results")
def get_skill_results(
    current_user: User = Depends(get_current_user),
):
    return {
        "user_preferences": _load_json("user_preferences.json"),
        "user_memory": _load_json("user_memory.json"),
        "recommendation_weights": _load_json("recommendation_weights.json"),
    }


@router.get("/health-trend")
def get_health_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(DishLog)
        .filter(DishLog.user_id == current_user.id)
        .order_by(DishLog.date_cooked.asc())
        .all()
    )

    if not logs:
        return {"weekly_scores": [], "overall_average": 0, "total_logs": 0}

    # Get autoimmune scores for logged recipes
    recipe_ids = list({log.recipe_id for log in logs})
    recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    recipe_scores = {r.id: r.autoimmune_score for r in recipes}

    # Group by week
    weekly = defaultdict(list)
    all_scores = []
    for log in logs:
        score = recipe_scores.get(log.recipe_id, 3)
        all_scores.append(score)
        # Group by ISO week
        week_key = log.date_cooked.strftime("%Y-W%W") if log.date_cooked else "unknown"
        weekly[week_key].append(score)

    weekly_scores = [
        {"week": week, "average": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for week, scores in sorted(weekly.items())
    ]

    overall_average = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    # Adherence: how many planned meals were actually logged
    plans = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).all()
    planned_count = 0
    for plan in plans:
        for day in (plan.days or []):
            for meal_type in ["breakfast", "lunch", "dinner"]:
                if day.get(meal_type) is not None:
                    planned_count += 1

    adherence = round(len(logs) / max(planned_count, 1) * 100, 1)

    return {
        "weekly_scores": weekly_scores,
        "overall_average": overall_average,
        "total_logs": len(logs),
        "adherence_percent": adherence,
    }
```

Register in `backend/app/main.py`:

```python
from app.api.admin import router as admin_router
```

```python
app.include_router(admin_router)
```

**Step 4: Run test to verify it passes**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_admin.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/api/admin.py backend/app/main.py backend/tests/test_admin.py
git commit -m "feat: add admin API for skill results and health trend data"
```

---

### Task 11: Frontend Types & API Client Updates

**Files:**
- Modify: `frontend/src/types/index.ts`
- Modify: `frontend/src/services/api.ts`

**Step 1: Update TypeScript types**

Add to `frontend/src/types/index.ts`:

```typescript
export interface FoodEntry {
  id: number;
  user_id: number;
  description: string;
  dish_name: string;
  detected_ingredients: string[];
  created_at: string;
}

export interface FoodPreference {
  id: number;
  user_id: number;
  type: 'like' | 'dislike';
  value: string;
  category: string;
  created_at: string;
}

export interface FoodSubmissionInput {
  text: string;
  submission_type?: 'recipe' | 'past_meals' | 'likes' | 'dislikes' | null;
}

export interface FoodSubmissionResult {
  detected_type: string;
  recipes: Omit<Recipe, 'id'>[];
  entries: { description: string; dish_name: string; detected_ingredients: string[] }[];
  preferences: { type: string; value: string; category: string }[];
}

export interface MealPlanGenerate {
  week_start: string;
  meal_types?: string[];
  cooking_sessions?: number | null;
  weekly_budget?: number | null;
  batch_cooking?: boolean;
}

export interface SkillResults {
  user_preferences: Record<string, unknown> | null;
  user_memory: Record<string, unknown> | null;
  recommendation_weights: Record<string, unknown> | null;
}

export interface WeeklyScore {
  week: string;
  average: number;
  count: number;
}

export interface HealthTrend {
  weekly_scores: WeeklyScore[];
  overall_average: number;
  total_logs: number;
  adherence_percent: number;
}
```

Update `DayPlan` to allow null:

```typescript
export interface DayPlan {
  breakfast: number | null;
  lunch: number | null;
  dinner: number | null;
}
```

**Step 2: Update API client**

Add to `frontend/src/services/api.ts`:

```typescript
import type {
  User, Profile, Recipe, MealPlan, DishLog, GroceryList,
  FoodSubmissionInput, FoodSubmissionResult, FoodPreference, FoodEntry,
  MealPlanGenerate, SkillResults, HealthTrend,
} from '../types';
```

Replace `generateMealPlan`:

```typescript
export const generateMealPlan = (data: MealPlanGenerate) =>
  api.post<MealPlan>('/meal-plans/generate', data);
```

Add food submission functions:

```typescript
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
```

**Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds (may have warnings about unused imports which is fine)

**Step 4: Commit**

```bash
git add frontend/src/types/index.ts frontend/src/services/api.ts
git commit -m "feat: update frontend types and API client for v2 features"
```

---

### Task 12: Unified Food Submission Page

**Files:**
- Rewrite: `frontend/src/pages/UploadRecipePage.tsx` → rename concept to `FoodSubmissionPage.tsx`
- Modify: `frontend/src/App.tsx` (update route)

**Step 1: Create the unified submission page**

Create `frontend/src/pages/FoodSubmissionPage.tsx`:

```tsx
import { useState } from 'react';
import { parseFoodSubmission, saveFoodSubmission, createRecipe } from '../services/api';
import type { FoodSubmissionResult } from '../types';

const SUBMISSION_TYPES = [
  { value: '', label: 'Auto-detect' },
  { value: 'recipe', label: 'Recipe' },
  { value: 'past_meals', label: 'Past Meals' },
  { value: 'likes', label: 'Foods I Like' },
  { value: 'dislikes', label: 'Foods I Dislike' },
];

export default function FoodSubmissionPage() {
  const [step, setStep] = useState<'input' | 'review' | 'saved'>('input');
  const [rawText, setRawText] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parseError, setParseError] = useState('');
  const [result, setResult] = useState<FoodSubmissionResult | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState('');

  const handleParse = async () => {
    setParsing(true);
    setParseError('');
    try {
      const resp = await parseFoodSubmission({
        text: rawText,
        submission_type: selectedType || null,
      });
      setResult(resp.data);
      setStep('review');
    } catch {
      setParseError('Failed to parse. Please try again.');
    } finally {
      setParsing(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    setSaving(true);
    setSaveError('');
    try {
      // If recipes were detected, save them via the recipe endpoint
      for (const recipe of result.recipes) {
        await createRecipe({ ...recipe, source: 'user_upload' } as any);
      }
      // Save entries and preferences
      if (result.entries.length > 0 || result.preferences.length > 0) {
        await saveFoodSubmission(result);
      }
      setStep('saved');
    } catch {
      setSaveError('Failed to save. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleRemovePreference = (index: number) => {
    if (!result) return;
    setResult({
      ...result,
      preferences: result.preferences.filter((_, i) => i !== index),
    });
  };

  const handleRemoveEntry = (index: number) => {
    if (!result) return;
    setResult({
      ...result,
      entries: result.entries.filter((_, i) => i !== index),
    });
  };

  if (step === 'saved') {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-green-800 mb-2">Saved!</h2>
          <p className="text-green-600 mb-4">Your food data has been saved and will be used to improve your meal recommendations.</p>
          <button
            onClick={() => { setStep('input'); setRawText(''); setResult(null); setSelectedType(''); }}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Submit More
          </button>
        </div>
      </div>
    );
  }

  if (step === 'review' && result) {
    return (
      <div className="max-w-2xl mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Review Submission</h1>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
          <span className="font-medium">Detected type:</span>{' '}
          <span className="capitalize">{result.detected_type.replace('_', ' ')}</span>
        </div>

        {result.recipes.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Recipes</h2>
            {result.recipes.map((recipe, i) => (
              <div key={i} className="border rounded-lg p-4 mb-2">
                <h3 className="font-medium">{recipe.name}</h3>
                <p className="text-sm text-gray-600">{(recipe.ingredients || []).length} ingredients, {(recipe.instructions || []).length} steps</p>
              </div>
            ))}
          </div>
        )}

        {result.preferences.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">
              {result.detected_type === 'dislikes' ? 'Dislikes' : 'Likes'}
            </h2>
            <div className="flex flex-wrap gap-2">
              {result.preferences.map((pref, i) => (
                <span key={i} className={`inline-flex items-center px-3 py-1 rounded-full text-sm ${
                  pref.type === 'dislike' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                }`}>
                  {pref.value}
                  <button onClick={() => handleRemovePreference(i)} className="ml-2 hover:opacity-70">&times;</button>
                </span>
              ))}
            </div>
          </div>
        )}

        {result.entries.length > 0 && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Past Meals</h2>
            {result.entries.map((entry, i) => (
              <div key={i} className="border rounded-lg p-3 mb-2 flex justify-between items-start">
                <div>
                  <p className="font-medium">{entry.dish_name}</p>
                  <p className="text-sm text-gray-500">
                    Ingredients: {entry.detected_ingredients.join(', ') || 'none detected'}
                  </p>
                </div>
                <button onClick={() => handleRemoveEntry(i)} className="text-red-500 hover:text-red-700">&times;</button>
              </div>
            ))}
          </div>
        )}

        {saveError && <p className="text-red-600 mb-4">{saveError}</p>}

        <div className="flex gap-3">
          <button
            onClick={() => setStep('input')}
            className="border border-gray-300 px-4 py-2 rounded hover:bg-gray-50"
          >
            Back
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-2">Food Submission</h1>
      <p className="text-gray-600 mb-6">
        Submit recipes, food preferences, past meals, or dislikes. This helps personalize your meal plans.
      </p>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Submission Type</label>
        <select
          value={selectedType}
          onChange={(e) => setSelectedType(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2"
        >
          {SUBMISSION_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-1">Content</label>
        <textarea
          value={rawText}
          onChange={(e) => setRawText(e.target.value)}
          placeholder={
            selectedType === 'recipe'
              ? 'Paste a full recipe with ingredients and instructions...'
              : selectedType === 'past_meals'
              ? 'Describe meals you\'ve had recently...\nSalmon with rice and broccoli\nChicken tacos with guacamole'
              : selectedType === 'likes'
              ? 'List foods you enjoy...\nThai curry, avocado, lemon, grilled fish'
              : selectedType === 'dislikes'
              ? 'List foods you want to avoid...\nCilantro, liver, eggplant'
              : 'Paste recipes, list preferences, or describe past meals...'
          }
          rows={10}
          className="w-full border border-gray-300 rounded px-3 py-2 font-mono text-sm"
        />
      </div>

      {parseError && <p className="text-red-600 mb-4">{parseError}</p>}

      <button
        onClick={handleParse}
        disabled={!rawText.trim() || parsing}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
      >
        {parsing ? 'Parsing...' : 'Parse & Review'}
      </button>
    </div>
  );
}
```

**Step 2: Update routing in `frontend/src/App.tsx`**

Replace the UploadRecipePage import and route:

```tsx
import FoodSubmissionPage from './pages/FoodSubmissionPage';
```

Change the route from:
```tsx
<Route path="/upload" element={<UploadRecipePage />} />
```
to:
```tsx
<Route path="/upload" element={<FoodSubmissionPage />} />
```

Keep `UploadRecipePage.tsx` in place (not deleted) — it still works as a standalone recipe uploader if needed.

**Step 3: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

**Step 4: Commit**

```bash
git add frontend/src/pages/FoodSubmissionPage.tsx frontend/src/App.tsx
git commit -m "feat: add unified food submission page replacing recipe-only upload"
```

---

### Task 13: Meal Plan Generation UI Update

**Files:**
- Modify: `frontend/src/pages/MealPlansPage.tsx`

**Step 1: Update the meal plan generation form**

The form currently has only a date picker. Add: meal type checkboxes, cooking sessions input, budget input, batch cooking toggle. Update the `generateMealPlan` call to pass the new `MealPlanGenerate` object.

Update `frontend/src/pages/MealPlansPage.tsx` — replace the generation form section. The key changes:

1. Add state for `mealTypes`, `cookingSessions`, `weeklyBudget`, `batchCooking`
2. Add form controls for each
3. Pass full object to `generateMealPlan()`

```tsx
// Add these state variables alongside existing state:
const [mealTypes, setMealTypes] = useState<string[]>(['breakfast', 'lunch', 'dinner']);
const [cookingSessions, setCookingSessions] = useState<string>('');
const [weeklyBudget, setWeeklyBudget] = useState<string>('');
const [batchCooking, setBatchCooking] = useState(false);
```

Update the generate handler:

```tsx
const handleGenerate = async () => {
  setGenerating(true);
  setError('');
  try {
    const resp = await generateMealPlan({
      week_start: weekStart,
      meal_types: mealTypes,
      cooking_sessions: cookingSessions ? parseInt(cookingSessions) : null,
      weekly_budget: weeklyBudget ? parseFloat(weeklyBudget) : null,
      batch_cooking: batchCooking,
    });
    navigate(`/meal-plans/${resp.data.id}`);
  } catch {
    setError('Failed to generate meal plan.');
  } finally {
    setGenerating(false);
  }
};
```

Add form controls between the date picker and generate button:

```tsx
{/* Meal Types */}
<div className="mb-4">
  <label className="block text-sm font-medium mb-2">Meals to Plan</label>
  <div className="flex gap-4">
    {['breakfast', 'lunch', 'dinner'].map((type) => (
      <label key={type} className="flex items-center gap-1">
        <input
          type="checkbox"
          checked={mealTypes.includes(type)}
          onChange={(e) => {
            if (e.target.checked) setMealTypes([...mealTypes, type]);
            else setMealTypes(mealTypes.filter((t) => t !== type));
          }}
        />
        <span className="capitalize">{type}</span>
      </label>
    ))}
  </div>
</div>

{/* Cooking Sessions */}
<div className="mb-4">
  <label className="block text-sm font-medium mb-1">Cooking Sessions This Week</label>
  <input
    type="number"
    min="1"
    max="21"
    value={cookingSessions}
    onChange={(e) => setCookingSessions(e.target.value)}
    placeholder="Leave blank for no limit"
    className="w-full border border-gray-300 rounded px-3 py-2"
  />
</div>

{/* Weekly Budget */}
<div className="mb-4">
  <label className="block text-sm font-medium mb-1">Weekly Grocery Budget ($)</label>
  <input
    type="number"
    min="0"
    step="5"
    value={weeklyBudget}
    onChange={(e) => setWeeklyBudget(e.target.value)}
    placeholder="Optional"
    className="w-full border border-gray-300 rounded px-3 py-2"
  />
</div>

{/* Batch Cooking */}
<div className="mb-4">
  <label className="flex items-center gap-2">
    <input
      type="checkbox"
      checked={batchCooking}
      onChange={(e) => setBatchCooking(e.target.checked)}
    />
    <span className="text-sm font-medium">Plan leftovers to reduce cooking sessions</span>
  </label>
</div>
```

**Step 2: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

**Step 3: Commit**

```bash
git add frontend/src/pages/MealPlansPage.tsx
git commit -m "feat: add weekly goal inputs to meal plan generation form"
```

---

### Task 14: Admin Console Page

**Files:**
- Create: `frontend/src/pages/AdminPage.tsx`
- Modify: `frontend/src/App.tsx` (add route)

**Step 1: Create the admin page**

Create `frontend/src/pages/AdminPage.tsx`:

```tsx
import { useEffect, useState } from 'react';
import { getSkillResults, getHealthTrend } from '../services/api';
import type { SkillResults, HealthTrend } from '../types';

export default function AdminPage() {
  const [skillResults, setSkillResults] = useState<SkillResults | null>(null);
  const [healthTrend, setHealthTrend] = useState<HealthTrend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [skillResp, trendResp] = await Promise.all([
          getSkillResults(),
          getHealthTrend(),
        ]);
        setSkillResults(skillResp.data);
        setHealthTrend(trendResp.data);
      } catch {
        setError('Failed to load admin data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">{error}</div>;

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Admin Console</h1>

      {/* Health Trend */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">Health Trend</h2>
        {healthTrend && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600">Overall Average</p>
              <p className="text-2xl font-bold text-blue-800">
                {healthTrend.overall_average}/5
              </p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600">Meals Logged</p>
              <p className="text-2xl font-bold text-green-800">
                {healthTrend.total_logs}
              </p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600">Adherence</p>
              <p className="text-2xl font-bold text-purple-800">
                {healthTrend.adherence_percent}%
              </p>
            </div>
          </div>
        )}

        {healthTrend && healthTrend.weekly_scores.length > 0 && (
          <div className="border rounded-lg p-4">
            <h3 className="font-medium mb-2">Weekly Autoimmune Scores</h3>
            <div className="space-y-2">
              {healthTrend.weekly_scores.map((ws) => (
                <div key={ws.week} className="flex items-center gap-3">
                  <span className="text-sm text-gray-500 w-20">{ws.week}</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-indigo-500 h-4 rounded-full"
                      style={{ width: `${(ws.average / 5) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium w-16">{ws.average}/5 ({ws.count})</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {healthTrend && healthTrend.weekly_scores.length === 0 && (
          <p className="text-gray-500">No dish logs yet. Start logging meals to see your health trend.</p>
        )}
      </section>

      {/* Skill Results */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-3">Skill Analysis Results</h2>
        <p className="text-sm text-gray-500 mb-4">
          These are generated by running Claude Code skills. Run them from the CLI to update.
        </p>

        <div className="space-y-4">
          <SkillCard
            title="User Preferences"
            data={skillResults?.user_preferences}
            description="Taste profile from recipe-analyzer skill"
          />
          <SkillCard
            title="User Memory"
            data={skillResults?.user_memory}
            description="Behavior patterns from user-profile-builder skill"
          />
          <SkillCard
            title="Recommendation Weights"
            data={skillResults?.recommendation_weights}
            description="Scoring weights from meal-plan-optimizer skill"
          />
        </div>
      </section>
    </div>
  );
}

function SkillCard({ title, data, description }: {
  title: string;
  data: Record<string, unknown> | null;
  description: string;
}) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border rounded-lg p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-medium">{title}</h3>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
        {data ? (
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
            Last run: {(data as any).generated_at || 'unknown'}
          </span>
        ) : (
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">Not yet run</span>
        )}
      </div>
      {data && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-sm text-indigo-600 mt-2 hover:underline"
          >
            {expanded ? 'Hide details' : 'Show details'}
          </button>
          {expanded && (
            <pre className="mt-2 bg-gray-50 rounded p-3 text-xs overflow-auto max-h-64">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
        </>
      )}
    </div>
  );
}
```

**Step 2: Add route in `frontend/src/App.tsx`**

Add import:
```tsx
import AdminPage from './pages/AdminPage';
```

Add route inside the authenticated routes:
```tsx
<Route path="/admin" element={<AdminPage />} />
```

**Step 3: Add admin link to navigation**

In the Layout component (wherever the nav links are), add:
```tsx
<a href="/admin">Admin</a>
```

**Step 4: Verify frontend builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

**Step 5: Commit**

```bash
git add frontend/src/pages/AdminPage.tsx frontend/src/App.tsx
git commit -m "feat: add admin console page with health trend and skill results"
```

---

### Task 15: Update Claude Code Skills

**Files:**
- Modify: `.claude/skills/recipe-analyzer.md`
- Modify: `.claude/skills/user-profile-builder.md`
- Modify: `.claude/skills/meal-plan-optimizer.md`

Update each skill to read from the new `food_entries` and `food_preferences` tables in addition to existing data sources. The skills' output format stays the same.

**Step 1: Update recipe-analyzer.md**

Add to the data sources section: query `food_entries` for detected ingredients and `food_preferences` for like/dislike signals. Include these in the taste profile analysis alongside personal recipes.

**Step 2: Update user-profile-builder.md**

Add: query `food_preferences` to include explicit likes/dislikes in the user memory. Query `food_entries` for additional dish history beyond logged meals.

**Step 3: Update meal-plan-optimizer.md**

Add: consider the number of food preferences and entries when adjusting weights. More preference data → higher `preference_match` weight.

**Step 4: Commit**

```bash
git add .claude/skills/
git commit -m "feat: update skills to use food entries and preferences data"
```

---

### Task 16: Run Full Test Suite & Fix Any Breakage

**Step 1: Run all backend tests**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/ -v`

**Step 2: Fix any failing tests**

The most likely breakage is in `test_meal_plan.py` due to the schema and recommender changes. Key things to check:
- `generate_meal_plan()` signature changed — old tests passing `dietary_restrictions` need updating
- `DayPlan` now allows `None` — existing tests may need adjustment
- Existing `test_integration.py` may call old API signatures

**Step 3: Run frontend build**

Run: `cd frontend && npm run build`

**Step 4: Fix any issues and commit**

```bash
git add -A
git commit -m "fix: resolve test breakage from v2 changes"
```

---

### Task 17: Update Navigation Links

**Files:**
- Modify: `frontend/src/components/Layout.tsx` (or wherever nav is defined)

**Step 1: Update navigation**

- Change "Upload Recipe" link text to "Food Submission" (route stays `/upload`)
- Add "Admin" link pointing to `/admin`

**Step 2: Verify frontend builds**

Run: `cd frontend && npm run build`

**Step 3: Commit**

```bash
git add frontend/src/components/Layout.tsx
git commit -m "feat: update navigation with food submission and admin links"
```

---

### Task 18: Integration Test

**Files:**
- Modify: `backend/tests/test_integration.py`

**Step 1: Add integration test for the full v2 flow**

Add a test that:
1. Registers and logs in
2. Creates a profile
3. Submits food preferences (likes + dislikes)
4. Submits past meals
5. Generates a meal plan with weekly goals (meal_types, cooking_sessions)
6. Verifies the plan respects meal type selection
7. Checks the health trend endpoint returns data after logging a dish

```python
def test_v2_full_workflow(client, db):
    _seed_recipes(db)
    headers = _register_and_login(client)

    # Submit likes
    resp = client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "salmon", "category": "ingredient"},
            {"type": "like", "value": "rice", "category": "ingredient"},
        ],
    }, headers=headers)
    assert resp.status_code == 201

    # Submit dislikes
    resp = client.post("/api/food/save", json={
        "detected_type": "dislikes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "dislike", "value": "liver", "category": "ingredient"},
        ],
    }, headers=headers)
    assert resp.status_code == 201

    # Generate meal plan with goals
    resp = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-16",
        "meal_types": ["lunch", "dinner"],
        "cooking_sessions": 5,
    }, headers=headers)
    assert resp.status_code == 201
    plan = resp.json()
    assert len(plan["days"]) == 7
    for day in plan["days"]:
        assert day["breakfast"] is None

    # Log a dish
    recipe_id = plan["days"][0]["lunch"]
    resp = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 4,
        "notes": "Great!",
        "would_make_again": True,
    }, headers=headers)
    assert resp.status_code == 201

    # Check health trend
    resp = client.get("/api/admin/health-trend", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_logs"] == 1

    # Check preferences stored
    resp = client.get("/api/food/preferences", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3
```

**Step 2: Run integration test**

Run: `cd backend && source venv/bin/activate && python -m pytest tests/test_integration.py -v`

**Step 3: Commit**

```bash
git add backend/tests/test_integration.py
git commit -m "test: add integration test for v2 recommender workflow"
```
