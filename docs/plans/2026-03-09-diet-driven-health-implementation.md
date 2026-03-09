# Diet Driven Health — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a holistic diet recommendation web app that generates weekly meal plans, tracks adherence, and manages grocery lists — tailored for autoimmune health (Lupus/renal).

**Architecture:** Python FastAPI backend with SQLAlchemy ORM and SQLite database. React + TypeScript + Tailwind CSS frontend. Simple auth. Rule-based meal plan recommendations using a pre-seeded recipe database. Claude Code skills for offline user preference analysis.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, SQLite, React 18, TypeScript, Tailwind CSS, Vite, pytest, Vitest

**Design Doc:** `docs/plans/2026-03-09-diet-driven-health-design.md`

---

## Phase 1: Backend Foundation

### Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/config.py`
- Create: `backend/app/database.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/services/__init__.py`

**Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
alembic==1.13.0
pytest==8.3.0
httpx==0.27.0
```

**Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./diet_driven_health.db"
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()
```

**Step 3: Create database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 4: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

app = FastAPI(title="Diet Driven Health", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Step 5: Create empty `__init__.py` files**

Empty files for `app/`, `app/api/`, `app/models/`, `app/schemas/`, `app/services/`.

**Step 6: Verify the server starts**

Run:
```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload &
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend with FastAPI, SQLAlchemy, and SQLite"
```

---

### Task 2: User Model and Auth

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/services/auth.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth.py`

**Step 1: Create test fixtures in conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Step 2: Write failing auth tests**

```python
def test_register_user(client):
    response = client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "javier"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_user(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 400


def test_login(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "testpass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    response = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_get_current_user(client):
    client.post("/api/auth/register", json={
        "username": "javier",
        "password": "testpass123",
    })
    login = client.post("/api/auth/login", data={
        "username": "javier",
        "password": "testpass123",
    })
    token = login.json()["access_token"]
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}",
    })
    assert response.status_code == 200
    assert response.json()["username"] == "javier"
```

**Step 3: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_auth.py -v`
Expected: FAIL — modules don't exist yet

**Step 4: Create User model**

`backend/app/models/user.py`:
```python
from sqlalchemy import Column, Integer, String
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
```

Update `backend/app/models/__init__.py`:
```python
from app.models.user import User
```

**Step 5: Create User schemas**

`backend/app/schemas/user.py`:
```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

**Step 6: Create auth service**

`backend/app/services/auth.py`:
```python
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def get_user_from_token(db: Session, token: str) -> User | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    return db.query(User).filter(User.username == username).first()
```

**Step 7: Create auth API routes**

`backend/app/api/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_user_from_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    user = get_user_from_token(db, token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(username=user_in.username, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Step 8: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.auth import router as auth_router

app.include_router(auth_router)
```

**Step 9: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_auth.py -v`
Expected: All 5 tests PASS

**Step 10: Commit**

```bash
git add backend/
git commit -m "feat: add user model and auth (register, login, JWT)"
```

---

### Task 3: User Profile Model and API

**Files:**
- Create: `backend/app/models/profile.py`
- Create: `backend/app/schemas/profile.py`
- Create: `backend/app/api/profile.py`
- Create: `backend/tests/test_profile.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing profile tests**

`backend/tests/test_profile.py`:
```python
def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_profile(client):
    token = _register_and_login(client)
    response = client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus", "renal"],
        "health_goals": ["anti-inflammatory", "kidney-friendly"],
        "dietary_restrictions": ["low-sodium", "low-potassium"],
    }, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["skill_level"] == "intermediate"
    assert "lupus" in data["health_conditions"]


def test_get_profile(client):
    token = _register_and_login(client)
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=_auth(token))
    response = client.get("/api/profile", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["skill_level"] == "intermediate"


def test_update_profile(client):
    token = _register_and_login(client)
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=_auth(token))
    response = client.put("/api/profile", json={
        "skill_level": "advanced",
        "health_conditions": ["lupus", "renal"],
        "health_goals": ["anti-inflammatory", "kidney-friendly"],
        "dietary_restrictions": ["low-sodium", "low-potassium"],
    }, headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["skill_level"] == "advanced"


def test_get_profile_not_found(client):
    token = _register_and_login(client)
    response = client.get("/api/profile", headers=_auth(token))
    assert response.status_code == 404
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_profile.py -v`
Expected: FAIL

**Step 3: Create Profile model**

`backend/app/models/profile.py`:
```python
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    skill_level = Column(String, nullable=False, default="intermediate")
    health_conditions = Column(JSON, default=list)
    health_goals = Column(JSON, default=list)
    dietary_restrictions = Column(JSON, default=list)

    user = relationship("User", backref="profile")
```

Update `backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.profile import UserProfile
```

**Step 4: Create Profile schemas**

`backend/app/schemas/profile.py`:
```python
from pydantic import BaseModel


class ProfileCreate(BaseModel):
    skill_level: str = "intermediate"
    health_conditions: list[str] = []
    health_goals: list[str] = []
    dietary_restrictions: list[str] = []


class ProfileResponse(ProfileCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
```

**Step 5: Create Profile API routes**

`backend/app/api/profile.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile = UserProfile(user_id=current_user.id, **profile_in.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileResponse)
def update_profile(
    profile_in: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in profile_in.model_dump().items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
```

**Step 6: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.profile import router as profile_router

app.include_router(profile_router)
```

**Step 7: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_profile.py -v`
Expected: All 4 tests PASS

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add user profile model and CRUD API"
```

---

### Task 4: Recipe Model and CRUD API

**Files:**
- Create: `backend/app/models/recipe.py`
- Create: `backend/app/schemas/recipe.py`
- Create: `backend/app/api/recipes.py`
- Create: `backend/tests/test_recipes.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing recipe tests**

`backend/tests/test_recipes.py`:
```python
def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


SAMPLE_RECIPE = {
    "name": "Anti-Inflammatory Salmon Bowl",
    "description": "A kidney-friendly salmon bowl with turmeric rice",
    "ingredients": [
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "brown rice", "quantity": 1, "unit": "cup"},
        {"name": "turmeric", "quantity": 1, "unit": "tsp"},
    ],
    "instructions": ["Cook rice with turmeric", "Bake salmon at 400F for 12 min", "Assemble bowl"],
    "prep_time_minutes": 10,
    "cook_time_minutes": 25,
    "difficulty": "intermediate",
    "servings": 2,
    "tags": ["anti-inflammatory", "kidney-friendly"],
    "autoimmune_score": 5,
    "nutrition": {
        "calories": 450,
        "protein": 35,
        "sodium": 200,
        "potassium": 400,
        "phosphorus": 300,
    },
    "source": "seeded",
}


def test_create_recipe(client):
    token = _register_and_login(client)
    response = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Anti-Inflammatory Salmon Bowl"
    assert data["autoimmune_score"] == 5
    assert len(data["ingredients"]) == 3


def test_list_recipes(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_recipe(client):
    token = _register_and_login(client)
    created = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    recipe_id = created.json()["id"]
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["name"] == "Anti-Inflammatory Salmon Bowl"


def test_filter_recipes_by_tag(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    recipe2 = SAMPLE_RECIPE.copy()
    recipe2["name"] = "Simple Oatmeal"
    recipe2["tags"] = ["anti-inflammatory"]
    client.post("/api/recipes", json=recipe2, headers=_auth(token))
    response = client.get("/api/recipes?tag=kidney-friendly", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_recipes_by_difficulty(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes?difficulty=beginner", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_recipes_by_name(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes?search=salmon", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_recipes.py -v`
Expected: FAIL

**Step 3: Create Recipe model**

`backend/app/models/recipe.py`:
```python
from sqlalchemy import Column, Integer, String, JSON, Float
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, default="")
    ingredients = Column(JSON, nullable=False)  # list of {name, quantity, unit}
    instructions = Column(JSON, nullable=False)  # list of strings
    prep_time_minutes = Column(Integer, default=0)
    cook_time_minutes = Column(Integer, default=0)
    difficulty = Column(String, default="intermediate")  # beginner/intermediate/advanced
    servings = Column(Integer, default=2)
    tags = Column(JSON, default=list)  # anti-inflammatory, kidney-friendly, etc.
    autoimmune_score = Column(Integer, default=3)  # 1-5
    nutrition = Column(JSON, default=dict)  # {calories, protein, sodium, potassium, phosphorus}
    source = Column(String, default="seeded")  # seeded or personal
```

Update `backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.profile import UserProfile
from app.models.recipe import Recipe
```

**Step 4: Create Recipe schemas**

`backend/app/schemas/recipe.py`:
```python
from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str


class Nutrition(BaseModel):
    calories: int = 0
    protein: int = 0
    sodium: int = 0
    potassium: int = 0
    phosphorus: int = 0


class RecipeCreate(BaseModel):
    name: str
    description: str = ""
    ingredients: list[Ingredient]
    instructions: list[str]
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0
    difficulty: str = "intermediate"
    servings: int = 2
    tags: list[str] = []
    autoimmune_score: int = 3
    nutrition: Nutrition = Nutrition()
    source: str = "seeded"


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str
    ingredients: list[Ingredient]
    instructions: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: str
    servings: int
    tags: list[str]
    autoimmune_score: int
    nutrition: Nutrition
    source: str

    class Config:
        from_attributes = True
```

**Step 5: Create Recipe API routes**

`backend/app/api/recipes.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import RecipeCreate, RecipeResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(
    recipe_in: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe_data = recipe_in.model_dump()
    recipe_data["ingredients"] = [i.model_dump() if hasattr(i, "model_dump") else i for i in recipe_in.ingredients]
    recipe_data["nutrition"] = recipe_in.nutrition.model_dump() if hasattr(recipe_in.nutrition, "model_dump") else recipe_in.nutrition
    recipe = Recipe(**recipe_data)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("", response_model=list[RecipeResponse])
def list_recipes(
    tag: str | None = Query(None),
    difficulty: str | None = Query(None),
    search: str | None = Query(None),
    max_time: int | None = Query(None),
    min_score: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Recipe)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))
    if max_time:
        query = query.filter(
            (Recipe.prep_time_minutes + Recipe.cook_time_minutes) <= max_time
        )
    if min_score:
        query = query.filter(Recipe.autoimmune_score >= min_score)
    recipes = query.all()
    if tag:
        recipes = [r for r in recipes if tag in (r.tags or [])]
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
```

**Step 6: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.recipes import router as recipes_router

app.include_router(recipes_router)
```

**Step 7: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_recipes.py -v`
Expected: All 6 tests PASS

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add recipe model with CRUD API and filtering"
```

---

### Task 5: Seed Recipe Data

**Files:**
- Create: `backend/app/data/seed_recipes.json`
- Create: `backend/app/services/seed.py`
- Create: `backend/tests/test_seed.py`

**Step 1: Write failing seed test**

`backend/tests/test_seed.py`:
```python
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
    assert len(recipes) >= 20
    for recipe in recipes:
        assert "name" in recipe
        assert "ingredients" in recipe
        assert "instructions" in recipe
        assert "tags" in recipe
        assert "autoimmune_score" in recipe


def test_seed_database(db):
    seed_database(db)
    count = db.query(Recipe).count()
    assert count >= 20


def test_seed_database_idempotent(db):
    seed_database(db)
    seed_database(db)
    count = db.query(Recipe).count()
    assert count >= 20  # no duplicates
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_seed.py -v`
Expected: FAIL

**Step 3: Create seed_recipes.json**

`backend/app/data/seed_recipes.json`:

Create a JSON file with at least 20 autoimmune-friendly, kidney-conscious recipes. Each recipe must include all fields from the RecipeCreate schema. Focus on:
- Anti-inflammatory ingredients (salmon, turmeric, ginger, berries, leafy greens, olive oil)
- Kidney-friendly considerations (moderate sodium <600mg, controlled potassium <500mg, controlled phosphorus <400mg per serving)
- Mix of difficulties (beginner/intermediate/advanced)
- Mix of meal types suitable for breakfast, lunch, and dinner
- Realistic prep/cook times

> **Note to implementer:** Generate 20-30 diverse recipes. This file will be large. Use the design doc's nutritional guidelines (sodium, potassium, phosphorus are key renal markers). Tag each recipe appropriately.

**Step 4: Create seed service**

`backend/app/services/seed.py`:
```python
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
```

**Step 5: Add seed command to main.py**

Add a startup event or CLI command to seed on first run. Add to `backend/app/main.py`:
```python
from app.database import SessionLocal
from app.services.seed import seed_database

@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
```

**Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_seed.py -v`
Expected: All 4 tests PASS

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add seed recipe database with 20+ autoimmune-friendly recipes"
```

---

### Task 6: Dish Log Model and API

**Files:**
- Create: `backend/app/models/dish_log.py`
- Create: `backend/app/schemas/dish_log.py`
- Create: `backend/app/api/dish_log.py`
- Create: `backend/tests/test_dish_log.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing dish log tests**

`backend/tests/test_dish_log.py`:
```python
from tests.test_recipes import SAMPLE_RECIPE


def _setup(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    recipe = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=headers).json()
    return headers, recipe["id"]


def test_log_dish(client):
    headers, recipe_id = _setup(client)
    response = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Delicious and easy!",
        "would_make_again": True,
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["would_make_again"] is True


def test_list_dish_logs(client):
    headers, recipe_id = _setup(client)
    client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 4,
        "notes": "Good",
        "would_make_again": True,
    }, headers=headers)
    response = client.get("/api/dish-log", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_favorites(client):
    headers, recipe_id = _setup(client)
    client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Love it",
        "would_make_again": True,
    }, headers=headers)
    response = client.get("/api/dish-log/favorites", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_dish_log.py -v`
Expected: FAIL

**Step 3: Create DishLog model**

`backend/app/models/dish_log.py`:
```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class DishLog(Base):
    __tablename__ = "dish_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    date_cooked = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rating = Column(Integer, nullable=False)  # 1-5
    notes = Column(String, default="")
    would_make_again = Column(Boolean, default=True)

    user = relationship("User", backref="dish_logs")
    recipe = relationship("Recipe", backref="dish_logs")
```

Update `backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.profile import UserProfile
from app.models.recipe import Recipe
from app.models.dish_log import DishLog
```

**Step 4: Create DishLog schemas**

`backend/app/schemas/dish_log.py`:
```python
from datetime import datetime
from pydantic import BaseModel


class DishLogCreate(BaseModel):
    recipe_id: int
    rating: int  # 1-5
    notes: str = ""
    would_make_again: bool = True


class DishLogResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    date_cooked: datetime
    rating: int
    notes: str
    would_make_again: bool

    class Config:
        from_attributes = True
```

**Step 5: Create DishLog API routes**

`backend/app/api/dish_log.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dish_log import DishLog
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.dish_log import DishLogCreate, DishLogResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/dish-log", tags=["dish-log"])


@router.post("", response_model=DishLogResponse, status_code=201)
def log_dish(
    log_in: DishLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == log_in.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    log = DishLog(user_id=current_user.id, **log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[DishLogResponse])
def list_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(DishLog).filter(DishLog.user_id == current_user.id).order_by(DishLog.date_cooked.desc()).all()


@router.get("/favorites", response_model=list[DishLogResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(DishLog)
        .filter(DishLog.user_id == current_user.id, DishLog.rating >= 4, DishLog.would_make_again == True)
        .order_by(DishLog.rating.desc())
        .all()
    )
```

**Step 6: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.dish_log import router as dish_log_router

app.include_router(dish_log_router)
```

**Step 7: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_dish_log.py -v`
Expected: All 3 tests PASS

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: add dish log model and API (log, list, favorites)"
```

---

### Task 7: Meal Plan Model and Generator

**Files:**
- Create: `backend/app/models/meal_plan.py`
- Create: `backend/app/schemas/meal_plan.py`
- Create: `backend/app/services/recommender.py`
- Create: `backend/app/api/meal_plans.py`
- Create: `backend/tests/test_meal_plan.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing meal plan tests**

`backend/tests/test_meal_plan.py`:
```python
from app.models.recipe import Recipe
from app.services.recommender import generate_meal_plan


def _register_login_and_profile(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=headers)
    return headers


def _seed_recipes(db):
    """Add enough recipes for a week of meal plans."""
    for i in range(25):
        recipe = Recipe(
            name=f"Recipe {i}",
            description=f"Test recipe {i}",
            ingredients=[{"name": "ingredient", "quantity": 1, "unit": "cup"}],
            instructions=["Step 1"],
            prep_time_minutes=15,
            cook_time_minutes=20,
            difficulty="intermediate",
            servings=2,
            tags=["anti-inflammatory"],
            autoimmune_score=4,
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        )
        db.add(recipe)
    db.commit()


def test_generate_meal_plan_service(db):
    _seed_recipes(db)
    plan = generate_meal_plan(db, skill_level="intermediate", dietary_restrictions=["low-sodium"], tags=["anti-inflammatory"])
    assert len(plan) == 7  # 7 days
    for day in plan:
        assert "breakfast" in day
        assert "lunch" in day
        assert "dinner" in day


def test_generate_meal_plan_no_repeats(db):
    _seed_recipes(db)
    plan = generate_meal_plan(db, skill_level="intermediate", dietary_restrictions=[], tags=[])
    recipe_ids = []
    for day in plan:
        for meal in ["breakfast", "lunch", "dinner"]:
            recipe_ids.append(day[meal])
    assert len(recipe_ids) == len(set(recipe_ids))  # all unique


def test_create_meal_plan_api(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    response = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["days"]) == 7


def test_list_meal_plans(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    response = client.get("/api/meal-plans", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_swap_meal(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    created = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    plan_id = created.json()["id"]
    original_recipe = created.json()["days"][0]["breakfast"]
    response = client.put(f"/api/meal-plans/{plan_id}/swap", json={
        "day_index": 0,
        "meal_type": "breakfast",
    }, headers=headers)
    assert response.status_code == 200
    new_recipe = response.json()["days"][0]["breakfast"]
    assert new_recipe != original_recipe
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_meal_plan.py -v`
Expected: FAIL

**Step 3: Create recommender service**

`backend/app/services/recommender.py`:
```python
import random

from sqlalchemy.orm import Session

from app.models.recipe import Recipe


def generate_meal_plan(
    db: Session,
    skill_level: str = "intermediate",
    dietary_restrictions: list[str] | None = None,
    tags: list[str] | None = None,
) -> list[dict]:
    """Generate a 7-day meal plan. Returns list of dicts with breakfast/lunch/dinner recipe IDs."""
    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed_difficulties = difficulty_map.get(skill_level, ["beginner", "intermediate"])

    query = db.query(Recipe).filter(Recipe.difficulty.in_(allowed_difficulties))
    recipes = query.all()

    if tags:
        recipes = [r for r in recipes if any(t in (r.tags or []) for t in tags)]

    if len(recipes) < 21:
        # Not enough recipes for a full unique plan; allow repeats across days
        pass

    random.shuffle(recipes)
    plan = []
    used_ids = set()
    recipe_pool = list(recipes)

    for day in range(7):
        day_meals = {}
        for meal_type in ["breakfast", "lunch", "dinner"]:
            # Try to find an unused recipe
            chosen = None
            for r in recipe_pool:
                if r.id not in used_ids:
                    chosen = r
                    break
            if chosen is None:
                # Reset pool if we run out
                chosen = random.choice(recipe_pool)
            used_ids.add(chosen.id)
            day_meals[meal_type] = chosen.id
        plan.append(day_meals)

    return plan


def get_swap_recipe(
    db: Session,
    excluded_ids: list[int],
    skill_level: str = "intermediate",
) -> int | None:
    """Get a single recipe ID not in excluded_ids."""
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
    return random.choice(recipes).id
```

**Step 4: Create MealPlan model**

`backend/app/models/meal_plan.py`:
```python
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(String, nullable=False)  # ISO date string YYYY-MM-DD
    days = Column(JSON, nullable=False)  # list of 7 dicts: {breakfast: id, lunch: id, dinner: id}

    user = relationship("User", backref="meal_plans")
```

Update `backend/app/models/__init__.py`:
```python
from app.models.user import User
from app.models.profile import UserProfile
from app.models.recipe import Recipe
from app.models.dish_log import DishLog
from app.models.meal_plan import MealPlan
```

**Step 5: Create MealPlan schemas**

`backend/app/schemas/meal_plan.py`:
```python
from pydantic import BaseModel


class MealPlanGenerate(BaseModel):
    week_start: str  # YYYY-MM-DD


class DayPlan(BaseModel):
    breakfast: int
    lunch: int
    dinner: int


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    week_start: str
    days: list[DayPlan]

    class Config:
        from_attributes = True


class MealSwap(BaseModel):
    day_index: int  # 0-6
    meal_type: str  # breakfast, lunch, dinner
```

**Step 6: Create MealPlan API routes**

`backend/app/api/meal_plans.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
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
    restrictions = profile.dietary_restrictions if profile else []
    goals = profile.health_goals if profile else []

    days = generate_meal_plan(db, skill_level=skill_level, dietary_restrictions=restrictions, tags=goals)
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
    all_ids = [days[d][m] for d in range(7) for m in ["breakfast", "lunch", "dinner"]]

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    skill_level = profile.skill_level if profile else "intermediate"

    new_id = get_swap_recipe(db, excluded_ids=all_ids, skill_level=skill_level)
    if new_id is None:
        raise HTTPException(status_code=400, detail="No alternative recipes available")

    days[swap.day_index] = dict(days[swap.day_index])
    days[swap.day_index][swap.meal_type] = new_id
    plan.days = days
    db.commit()
    db.refresh(plan)
    return plan
```

**Step 7: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.meal_plans import router as meal_plans_router

app.include_router(meal_plans_router)
```

**Step 8: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_meal_plan.py -v`
Expected: All 5 tests PASS

**Step 9: Commit**

```bash
git add backend/
git commit -m "feat: add meal plan generator with rule-based recommendations and swap"
```

---

### Task 8: Grocery List Generator

**Files:**
- Create: `backend/app/services/grocery.py`
- Create: `backend/app/schemas/grocery.py`
- Create: `backend/app/api/grocery.py`
- Create: `backend/tests/test_grocery.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing grocery tests**

`backend/tests/test_grocery.py`:
```python
from app.services.grocery import consolidate_ingredients, estimate_cost, STORE_SECTIONS


def test_consolidate_ingredients():
    ingredients = [
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "brown rice", "quantity": 1, "unit": "cup"},
        {"name": "brown rice", "quantity": 2, "unit": "cup"},
    ]
    result = consolidate_ingredients(ingredients)
    assert len(result) == 2
    salmon = next(i for i in result if i["name"] == "salmon fillet")
    assert salmon["quantity"] == 12
    rice = next(i for i in result if i["name"] == "brown rice")
    assert rice["quantity"] == 3


def test_estimate_cost():
    items = [
        {"name": "salmon fillet", "quantity": 12, "unit": "oz"},
        {"name": "brown rice", "quantity": 3, "unit": "cup"},
    ]
    total = estimate_cost(items)
    assert total > 0


def test_store_sections():
    assert "produce" in STORE_SECTIONS
    assert "protein" in STORE_SECTIONS


def test_grocery_api(client, db):
    # Setup: register, login, create profile, seed recipes, generate plan
    from tests.test_meal_plan import _seed_recipes, _register_login_and_profile
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    created = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    plan_id = created.json()["id"]
    response = client.get(f"/api/grocery/{plan_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_estimated_cost" in data
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_grocery.py -v`
Expected: FAIL

**Step 3: Create grocery service**

`backend/app/services/grocery.py`:
```python
from sqlalchemy.orm import Session

from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe

STORE_SECTIONS = {
    "produce": ["lettuce", "spinach", "kale", "tomato", "onion", "garlic", "ginger",
                 "avocado", "lemon", "lime", "bell pepper", "cucumber", "carrot",
                 "celery", "broccoli", "cauliflower", "sweet potato", "zucchini",
                 "berries", "blueberries", "strawberries", "apple", "banana"],
    "protein": ["salmon", "chicken", "turkey", "beef", "shrimp", "tofu", "egg",
                "tuna", "cod", "tilapia"],
    "dairy": ["milk", "yogurt", "cheese", "butter", "cream"],
    "grains": ["rice", "oats", "quinoa", "bread", "pasta", "tortilla", "flour"],
    "pantry": ["olive oil", "coconut oil", "turmeric", "cumin", "paprika",
               "cinnamon", "honey", "maple syrup", "soy sauce", "vinegar",
               "salt", "pepper", "broth", "stock", "beans", "lentils",
               "chickpeas", "nuts", "almonds", "walnuts"],
    "frozen": ["frozen berries", "frozen vegetables"],
    "other": [],
}

# Rough cost estimates per unit (USD)
COST_ESTIMATES = {
    "oz": 0.50,
    "lb": 5.00,
    "cup": 1.00,
    "tbsp": 0.15,
    "tsp": 0.05,
    "piece": 1.00,
    "clove": 0.10,
    "can": 1.50,
    "bunch": 2.00,
    "head": 2.50,
    "slice": 0.30,
}


def consolidate_ingredients(ingredients: list[dict]) -> list[dict]:
    """Merge duplicate ingredients by name+unit, summing quantities."""
    consolidated = {}
    for item in ingredients:
        key = (item["name"].lower().strip(), item["unit"].lower().strip())
        if key in consolidated:
            consolidated[key]["quantity"] += item["quantity"]
        else:
            consolidated[key] = {
                "name": item["name"],
                "quantity": item["quantity"],
                "unit": item["unit"],
            }
    return list(consolidated.values())


def categorize_item(name: str) -> str:
    """Assign a store section to an ingredient."""
    name_lower = name.lower()
    for section, keywords in STORE_SECTIONS.items():
        if section == "other":
            continue
        for keyword in keywords:
            if keyword in name_lower:
                return section
    return "other"


def estimate_cost(items: list[dict]) -> float:
    """Rough cost estimate for a list of ingredients."""
    total = 0.0
    for item in items:
        unit = item["unit"].lower().strip()
        per_unit = COST_ESTIMATES.get(unit, 1.00)
        total += item["quantity"] * per_unit
    return round(total, 2)


def generate_grocery_list(db: Session, plan_id: int, user_id: int) -> dict:
    """Generate a consolidated grocery list from a meal plan."""
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_id, MealPlan.user_id == user_id
    ).first()
    if not plan:
        return None

    all_ingredients = []
    recipe_ids = set()
    for day in plan.days:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            recipe_ids.add(day[meal_type])

    recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            all_ingredients.append(ingredient)

    consolidated = consolidate_ingredients(all_ingredients)

    items = []
    for item in consolidated:
        items.append({
            **item,
            "section": categorize_item(item["name"]),
            "estimated_cost": round(item["quantity"] * COST_ESTIMATES.get(item["unit"].lower().strip(), 1.00), 2),
            "checked": False,
        })

    items.sort(key=lambda x: x["section"])

    return {
        "meal_plan_id": plan_id,
        "items": items,
        "total_estimated_cost": estimate_cost(consolidated),
    }
```

**Step 4: Create grocery schemas and API**

`backend/app/schemas/grocery.py`:
```python
from pydantic import BaseModel


class GroceryItem(BaseModel):
    name: str
    quantity: float
    unit: str
    section: str
    estimated_cost: float
    checked: bool = False


class GroceryListResponse(BaseModel):
    meal_plan_id: int
    items: list[GroceryItem]
    total_estimated_cost: float
```

`backend/app/api/grocery.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.grocery import GroceryListResponse
from app.services.grocery import generate_grocery_list
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/grocery", tags=["grocery"])


@router.get("/{plan_id}", response_model=GroceryListResponse)
def get_grocery_list(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = generate_grocery_list(db, plan_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return result
```

**Step 5: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.grocery import router as grocery_router

app.include_router(grocery_router)
```

**Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_grocery.py -v`
Expected: All 4 tests PASS

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add grocery list generator with consolidation and cost estimates"
```

---

### Task 9: Recipe Upload Parser

**Files:**
- Create: `backend/app/services/recipe_parser.py`
- Create: `backend/app/api/upload.py`
- Create: `backend/app/schemas/upload.py`
- Create: `backend/tests/test_parser.py`
- Modify: `backend/app/main.py`

**Step 1: Write failing parser tests**

`backend/tests/test_parser.py`:
```python
from app.services.recipe_parser import parse_recipe_text


def test_parse_basic_recipe():
    text = """
    Turmeric Chicken

    Ingredients:
    - 1 lb chicken breast
    - 2 tsp turmeric
    - 1 tbsp olive oil
    - 1/2 tsp salt

    Instructions:
    1. Season chicken with turmeric and salt
    2. Heat olive oil in a pan
    3. Cook chicken for 6 minutes per side
    """
    result = parse_recipe_text(text)
    assert result["name"] == "Turmeric Chicken"
    assert len(result["ingredients"]) >= 3
    assert len(result["instructions"]) >= 3


def test_parse_recipe_without_headers():
    text = """
    Simple Salmon

    6 oz salmon fillet
    1 tsp lemon juice
    salt and pepper

    Bake at 400F for 12 minutes.
    Squeeze lemon on top.
    """
    result = parse_recipe_text(text)
    assert result["name"] != ""
    assert len(result["ingredients"]) >= 1


def test_parse_returns_all_fields():
    text = """
    Test Recipe

    Ingredients:
    - 1 cup rice

    Instructions:
    1. Cook rice
    """
    result = parse_recipe_text(text)
    assert "name" in result
    assert "ingredients" in result
    assert "instructions" in result
    assert "source" in result
    assert result["source"] == "personal"


def test_upload_api(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/upload/parse", json={
        "text": """
        My Favorite Soup

        Ingredients:
        - 2 cups chicken broth
        - 1 cup carrots, diced
        - 1/2 cup celery

        Instructions:
        1. Bring broth to boil
        2. Add vegetables
        3. Simmer for 20 minutes
        """,
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Favorite Soup"
```

**Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_parser.py -v`
Expected: FAIL

**Step 3: Create recipe parser service**

`backend/app/services/recipe_parser.py`:
```python
import re


def parse_recipe_text(text: str) -> dict:
    """Parse unstructured recipe text into a structured format.

    Returns a dict with name, ingredients, instructions, and source fields.
    This is a best-effort parser — user should review and correct the result.
    """
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    # Extract name: first non-empty line
    name = lines[0] if lines else "Untitled Recipe"

    # Find sections
    ingredients = []
    instructions = []
    current_section = None

    for line in lines[1:]:
        lower = line.lower()

        # Detect section headers
        if lower.startswith("ingredient"):
            current_section = "ingredients"
            continue
        elif lower.startswith("instruction") or lower.startswith("direction") or lower.startswith("method") or lower.startswith("steps"):
            current_section = "instructions"
            continue

        # Parse based on current section
        if current_section == "ingredients":
            ingredient = _parse_ingredient_line(line)
            if ingredient:
                ingredients.append(ingredient)
        elif current_section == "instructions":
            step = _parse_instruction_line(line)
            if step:
                instructions.append(step)
        else:
            # Try to auto-detect
            ingredient = _parse_ingredient_line(line)
            if ingredient and _looks_like_ingredient(line):
                if not current_section:
                    current_section = "ingredients"
                ingredients.append(ingredient)
            elif _looks_like_instruction(line):
                current_section = "instructions"
                step = _parse_instruction_line(line)
                if step:
                    instructions.append(step)

    return {
        "name": name,
        "description": "",
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": 0,
        "cook_time_minutes": 0,
        "difficulty": "intermediate",
        "servings": 2,
        "tags": [],
        "autoimmune_score": 3,
        "nutrition": {"calories": 0, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0},
        "source": "personal",
    }


def _parse_ingredient_line(line: str) -> dict | None:
    """Try to parse a line like '1 cup rice' or '- 2 tsp turmeric'."""
    # Remove leading bullet/dash/number
    cleaned = re.sub(r"^[-•*]\s*", "", line)
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned)

    # Match quantity + unit + name pattern
    match = re.match(
        r"(\d+(?:/\d+)?(?:\.\d+)?)\s*(cup|cups|tbsp|tsp|oz|lb|lbs|piece|pieces|clove|cloves|can|cans|bunch|head|slice|slices|g|kg|ml|l)s?\s+(.+)",
        cleaned,
        re.IGNORECASE,
    )
    if match:
        quantity_str = match.group(1)
        if "/" in quantity_str:
            parts = quantity_str.split("/")
            quantity = float(parts[0]) / float(parts[1])
        else:
            quantity = float(quantity_str)
        return {
            "name": match.group(3).strip().rstrip(","),
            "quantity": quantity,
            "unit": match.group(2).lower().rstrip("s"),
        }

    # Fallback: treat whole line as ingredient name with quantity 1
    if cleaned and not _looks_like_instruction(cleaned):
        return {"name": cleaned, "quantity": 1, "unit": "piece"}
    return None


def _parse_instruction_line(line: str) -> str | None:
    """Clean an instruction line."""
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", line)
    cleaned = re.sub(r"^[-•*]\s*", "", cleaned)
    return cleaned.strip() if cleaned.strip() else None


def _looks_like_ingredient(line: str) -> bool:
    """Heuristic: does this line look like an ingredient?"""
    return bool(re.match(r"^[-•*]?\s*\d", line)) or line.startswith("-")


def _looks_like_instruction(line: str) -> bool:
    """Heuristic: does this line look like an instruction?"""
    action_words = ["cook", "bake", "heat", "add", "mix", "stir", "pour", "place",
                    "bring", "simmer", "boil", "season", "serve", "cut", "dice",
                    "chop", "slice", "squeeze", "preheat", "combine", "whisk", "let"]
    lower = line.lower().lstrip("0123456789.-) ")
    return any(lower.startswith(word) for word in action_words)
```

**Step 4: Create upload schemas and API**

`backend/app/schemas/upload.py`:
```python
from pydantic import BaseModel

from app.schemas.recipe import RecipeCreate


class RecipeTextInput(BaseModel):
    text: str


class ParsedRecipeResponse(RecipeCreate):
    pass
```

`backend/app/api/upload.py`:
```python
from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.upload import RecipeTextInput, ParsedRecipeResponse
from app.services.recipe_parser import parse_recipe_text
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/parse", response_model=ParsedRecipeResponse)
def parse_recipe(
    input: RecipeTextInput,
    current_user: User = Depends(get_current_user),
):
    return parse_recipe_text(input.text)
```

**Step 5: Register router in main.py**

Add to `backend/app/main.py`:
```python
from app.api.upload import router as upload_router

app.include_router(upload_router)
```

**Step 6: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_parser.py -v`
Expected: All 4 tests PASS

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: add recipe text parser and upload API"
```

---

## Phase 2: Frontend

### Task 10: Frontend Scaffolding

**Files:**
- Create: `frontend/` (via Vite scaffold)
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: Scaffold React + TypeScript + Vite project**

Run:
```bash
cd /home/claude/diet_driven_health
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install react-router-dom axios
```

**Step 2: Configure Tailwind**

Update `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

Replace `frontend/src/index.css` with:
```css
@import "tailwindcss";
```

**Step 3: Create TypeScript types**

`frontend/src/types/index.ts`:
```typescript
export interface User {
  id: number;
  username: string;
}

export interface Profile {
  id: number;
  user_id: number;
  skill_level: string;
  health_conditions: string[];
  health_goals: string[];
  dietary_restrictions: string[];
}

export interface Ingredient {
  name: string;
  quantity: number;
  unit: string;
}

export interface Nutrition {
  calories: number;
  protein: number;
  sodium: number;
  potassium: number;
  phosphorus: number;
}

export interface Recipe {
  id: number;
  name: string;
  description: string;
  ingredients: Ingredient[];
  instructions: string[];
  prep_time_minutes: number;
  cook_time_minutes: number;
  difficulty: string;
  servings: number;
  tags: string[];
  autoimmune_score: number;
  nutrition: Nutrition;
  source: string;
}

export interface DayPlan {
  breakfast: number;
  lunch: number;
  dinner: number;
}

export interface MealPlan {
  id: number;
  user_id: number;
  week_start: string;
  days: DayPlan[];
}

export interface DishLog {
  id: number;
  user_id: number;
  recipe_id: number;
  date_cooked: string;
  rating: number;
  notes: string;
  would_make_again: boolean;
}

export interface GroceryItem {
  name: string;
  quantity: number;
  unit: string;
  section: string;
  estimated_cost: number;
  checked: boolean;
}

export interface GroceryList {
  meal_plan_id: number;
  items: GroceryItem[];
  total_estimated_cost: number;
}
```

**Step 4: Create API service**

`frontend/src/services/api.ts`:
```typescript
import axios from 'axios';
import type {
  User, Profile, Recipe, MealPlan, DishLog, GroceryList,
} from '../types';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (username: string, password: string) =>
  api.post<User>('/auth/register', { username, password });

export const login = async (username: string, password: string) => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);
  const resp = await api.post<{ access_token: string }>('/auth/login', params);
  localStorage.setItem('token', resp.data.access_token);
  return resp.data;
};

export const getMe = () => api.get<User>('/auth/me');

export const logout = () => localStorage.removeItem('token');

// Profile
export const getProfile = () => api.get<Profile>('/profile');
export const createProfile = (data: Omit<Profile, 'id' | 'user_id'>) =>
  api.post<Profile>('/profile', data);
export const updateProfile = (data: Omit<Profile, 'id' | 'user_id'>) =>
  api.put<Profile>('/profile', data);

// Recipes
export const getRecipes = (params?: Record<string, string>) =>
  api.get<Recipe[]>('/recipes', { params });
export const getRecipe = (id: number) => api.get<Recipe>(`/recipes/${id}`);
export const createRecipe = (data: Omit<Recipe, 'id'>) =>
  api.post<Recipe>('/recipes', data);

// Meal Plans
export const generateMealPlan = (weekStart: string) =>
  api.post<MealPlan>('/meal-plans/generate', { week_start: weekStart });
export const getMealPlans = () => api.get<MealPlan[]>('/meal-plans');
export const getMealPlan = (id: number) => api.get<MealPlan>(`/meal-plans/${id}`);
export const swapMeal = (planId: number, dayIndex: number, mealType: string) =>
  api.put<MealPlan>(`/meal-plans/${planId}/swap`, { day_index: dayIndex, meal_type: mealType });

// Dish Log
export const logDish = (data: Omit<DishLog, 'id' | 'user_id' | 'date_cooked'>) =>
  api.post<DishLog>('/dish-log', data);
export const getDishLogs = () => api.get<DishLog[]>('/dish-log');
export const getFavorites = () => api.get<DishLog[]>('/dish-log/favorites');

// Grocery
export const getGroceryList = (planId: number) =>
  api.get<GroceryList>(`/grocery/${planId}`);

// Upload
export const parseRecipeText = (text: string) =>
  api.post<Recipe>('/upload/parse', { text });

export default api;
```

**Step 5: Set up basic App with routing**

`frontend/src/App.tsx`:
```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';

function App() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    getMe()
      .then(() => setLoggedIn(true))
      .catch(() => setLoggedIn(false));
  }, []);

  if (loggedIn === null) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={loggedIn ? <div>Dashboard (coming soon)</div> : <Navigate to="/login" />} />
          <Route path="/login" element={<div>Login (coming soon)</div>} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

**Step 6: Verify frontend builds and runs**

Run:
```bash
cd frontend && npm run build
```
Expected: Build succeeds with no errors

**Step 7: Commit**

```bash
git add frontend/
echo "node_modules/" >> .gitignore
git add .gitignore
git commit -m "feat: scaffold React frontend with TypeScript, Tailwind, and API client"
```

---

### Task 11: Login and Registration Pages

**Files:**
- Create: `frontend/src/pages/LoginPage.tsx`
- Create: `frontend/src/pages/RegisterPage.tsx`
- Create: `frontend/src/components/Layout.tsx`
- Modify: `frontend/src/App.tsx`

**Step 1: Create Layout component**

`frontend/src/components/Layout.tsx`:
```tsx
import { Link, useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

export default function Layout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-green-700">Diet Driven Health</Link>
          <div className="flex gap-4 text-sm">
            <Link to="/" className="text-gray-600 hover:text-green-700">Dashboard</Link>
            <Link to="/meal-plans" className="text-gray-600 hover:text-green-700">Meal Plans</Link>
            <Link to="/recipes" className="text-gray-600 hover:text-green-700">Recipes</Link>
            <Link to="/history" className="text-gray-600 hover:text-green-700">History</Link>
            <Link to="/profile" className="text-gray-600 hover:text-green-700">Profile</Link>
            <button onClick={handleLogout} className="text-red-500 hover:text-red-700">Logout</button>
          </div>
        </div>
      </nav>
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
```

**Step 2: Create LoginPage**

`frontend/src/pages/LoginPage.tsx`:
```tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../services/api';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/');
      window.location.reload();
    } catch {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-2xl font-bold text-green-700 mb-6 text-center">Diet Driven Health</h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <input
          type="text" placeholder="Username" value={username}
          onChange={e => setUsername(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
          Login
        </button>
        <p className="text-center text-sm mt-4">
          No account? <Link to="/register" className="text-green-600 hover:underline">Register</Link>
        </p>
      </form>
    </div>
  );
}
```

**Step 3: Create RegisterPage**

`frontend/src/pages/RegisterPage.tsx`:
```tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register, login } from '../services/api';

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(username, password);
      await login(username, password);
      navigate('/');
      window.location.reload();
    } catch {
      setError('Registration failed — username may be taken');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-2xl font-bold text-green-700 mb-6 text-center">Create Account</h1>
        {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
        <input
          type="text" placeholder="Username" value={username}
          onChange={e => setUsername(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={e => setPassword(e.target.value)}
          className="w-full border rounded px-3 py-2 mb-4"
        />
        <button type="submit" className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
          Register
        </button>
        <p className="text-center text-sm mt-4">
          Already have an account? <Link to="/login" className="text-green-600 hover:underline">Login</Link>
        </p>
      </form>
    </div>
  );
}
```

**Step 4: Update App.tsx with routes**

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { getMe } from './services/api';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

function App() {
  const [loggedIn, setLoggedIn] = useState<boolean | null>(null);

  useEffect(() => {
    getMe()
      .then(() => setLoggedIn(true))
      .catch(() => setLoggedIn(false));
  }, []);

  if (loggedIn === null) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={!loggedIn ? <LoginPage /> : <Navigate to="/" />} />
        <Route path="/register" element={!loggedIn ? <RegisterPage /> : <Navigate to="/" />} />
        <Route path="/*" element={
          loggedIn ? (
            <Layout>
              <Routes>
                <Route path="/" element={<div>Dashboard (coming next)</div>} />
                <Route path="/meal-plans" element={<div>Meal Plans (coming soon)</div>} />
                <Route path="/recipes" element={<div>Recipes (coming soon)</div>} />
                <Route path="/history" element={<div>History (coming soon)</div>} />
                <Route path="/profile" element={<div>Profile (coming soon)</div>} />
              </Routes>
            </Layout>
          ) : <Navigate to="/login" />
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

**Step 5: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds

**Step 6: Commit**

```bash
git add frontend/
git commit -m "feat: add login, register pages and navigation layout"
```

---

### Task 12: Dashboard Page

**Files:**
- Create: `frontend/src/pages/DashboardPage.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a dashboard showing: current week's meal plan summary, adherence stats (meals cooked vs planned), quick stats (average health score, dishes cooked this week). Use the `getMealPlans`, `getDishLogs`, and `getRecipes` API calls. Mobile-responsive with Tailwind grid/flex.

**Step 1: Create DashboardPage with meal plan overview and stats**

**Step 2: Wire into App.tsx routes**

**Step 3: Verify build, commit**

```bash
git commit -m "feat: add dashboard page with meal plan overview and stats"
```

---

### Task 13: Recipe Browser Page

**Files:**
- Create: `frontend/src/pages/RecipesPage.tsx`
- Create: `frontend/src/pages/RecipeDetailPage.tsx`
- Create: `frontend/src/components/RecipeCard.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a searchable/filterable recipe list with cards showing name, tags, difficulty, time, health score. Clicking a card opens a detail view with full ingredients, instructions, and nutritional breakdown. Include filter controls for tag, difficulty, max time, and min autoimmune score. Mobile-responsive.

**Step 1: Create RecipeCard component**
**Step 2: Create RecipesPage with search and filters**
**Step 3: Create RecipeDetailPage with full recipe view**
**Step 4: Add routes to App.tsx**
**Step 5: Verify build, commit**

```bash
git commit -m "feat: add recipe browser with search, filters, and detail view"
```

---

### Task 14: Meal Plan Page

**Files:**
- Create: `frontend/src/pages/MealPlansPage.tsx`
- Create: `frontend/src/pages/MealPlanDetailPage.tsx`
- Create: `frontend/src/components/MealPlanGrid.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a page to generate new meal plans (date picker for week start), view current/past plans in a 7-day grid (breakfast/lunch/dinner), and swap individual meals. The grid should show recipe names and be clickable to view recipe details. Mobile-responsive — stack days vertically on small screens.

**Step 1: Create MealPlanGrid component (7-day x 3-meal grid)**
**Step 2: Create MealPlansPage (list + generate button)**
**Step 3: Create MealPlanDetailPage (grid + swap buttons)**
**Step 4: Add routes to App.tsx**
**Step 5: Verify build, commit**

```bash
git commit -m "feat: add meal plan pages with generation, grid view, and swap"
```

---

### Task 15: Grocery List Page

**Files:**
- Create: `frontend/src/pages/GroceryListPage.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a grocery list view for a meal plan. Items grouped by store section with checkboxes. Show estimated cost per item and total. Mobile-optimized for use while shopping. Include a "print" or "share" button.

**Step 1: Create GroceryListPage with section grouping and checkboxes**
**Step 2: Add route to App.tsx**
**Step 3: Verify build, commit**

```bash
git commit -m "feat: add grocery list page with section grouping and cost estimates"
```

---

### Task 16: Dish History Page

**Files:**
- Create: `frontend/src/pages/DishHistoryPage.tsx`
- Create: `frontend/src/components/DishLogForm.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a dish history page showing logged dishes with ratings, dates, and notes. Include a form to log a new dish (select recipe, rate 1-5 stars, notes, would-make-again toggle). Add a "Favorites" tab that filters to top-rated dishes. Filterable by rating and date range.

**Step 1: Create DishLogForm component**
**Step 2: Create DishHistoryPage with list and favorites tab**
**Step 3: Add route to App.tsx**
**Step 4: Verify build, commit**

```bash
git commit -m "feat: add dish history page with rating form and favorites"
```

---

### Task 17: Profile Page

**Files:**
- Create: `frontend/src/pages/ProfilePage.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a profile page with editable fields: skill level (dropdown), health conditions (tag input), health goals (tag input), dietary restrictions (tag input). Show onboarding form if no profile exists. Save button calls create or update API.

**Step 1: Create ProfilePage with editable form**
**Step 2: Add route to App.tsx**
**Step 3: Verify build, commit**

```bash
git commit -m "feat: add profile page with onboarding and editable preferences"
```

---

### Task 18: Recipe Upload Page

**Files:**
- Create: `frontend/src/pages/UploadRecipePage.tsx`
- Modify: `frontend/src/App.tsx`

> **Note to implementer:** Build a page with a large textarea to paste recipe text. "Parse" button calls the parse API. Show the parsed result in an editable form (name, ingredients, instructions, tags, etc.). "Save" button calls createRecipe to save to DB. Preview the parsed result before saving.

**Step 1: Create UploadRecipePage with paste, parse, review, save flow**
**Step 2: Add route to App.tsx and nav link**
**Step 3: Verify build, commit**

```bash
git commit -m "feat: add recipe upload page with text parsing and review"
```

---

## Phase 3: Claude Code Skills

### Task 19: Recipe Analyzer Skill

**Files:**
- Create: `.claude/skills/recipe-analyzer.md`

> **Note to implementer:** Create a Claude Code skill that:
> 1. Reads the SQLite database to get all recipes marked as "personal"
> 2. Analyzes ingredient patterns, flavor profiles, and cuisine preferences
> 3. Writes analysis results to `backend/app/data/user_preferences.json`
>
> The skill file should describe the trigger, purpose, and exact steps for Claude Code to follow.

**Step 1: Write the skill file**
**Step 2: Test by running the skill manually**
**Step 3: Commit**

```bash
git commit -m "feat: add recipe-analyzer Claude Code skill"
```

---

### Task 20: User Profile Builder Skill

**Files:**
- Create: `.claude/skills/user-profile-builder.md`

> **Note to implementer:** Create a Claude Code skill that:
> 1. Reads dish logs, meal plan adherence data, and recipe ratings from the DB
> 2. Synthesizes into a user memory file capturing: favorite ingredients, preferred cuisines, cooking time preferences, health score trends, adherence patterns
> 3. Writes to `backend/app/data/user_memory.json`
> 4. This file is loaded by the recommender service to weight recipe selection

**Step 1: Write the skill file**
**Step 2: Commit**

```bash
git commit -m "feat: add user-profile-builder Claude Code skill"
```

---

### Task 21: Meal Plan Optimizer Skill

**Files:**
- Create: `.claude/skills/meal-plan-optimizer.md`

> **Note to implementer:** Create a Claude Code skill that:
> 1. Reads user memory file and dish log patterns
> 2. Suggests improvements to the recommender service's scoring weights
> 3. Updates `backend/app/data/recommendation_weights.json`
> 4. The recommender service loads these weights to improve future meal plans

**Step 1: Write the skill file**
**Step 2: Commit**

```bash
git commit -m "feat: add meal-plan-optimizer Claude Code skill"
```

---

## Phase 4: Integration and Polish

### Task 22: End-to-End Integration Test

**Files:**
- Create: `backend/tests/test_integration.py`

**Step 1: Write an integration test**

```python
def test_full_workflow(client, db):
    """Test the complete user journey: register -> profile -> generate plan -> grocery -> log dish."""
    # Register and login
    client.post("/api/auth/register", json={"username": "javier", "password": "test123"})
    resp = client.post("/api/auth/login", data={"username": "javier", "password": "test123"})
    headers = {"Authorization": f"Bearer " + resp.json()["access_token"]}

    # Create profile
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=headers)

    # Seed recipes (done automatically on startup, but add for test)
    from app.services.seed import seed_database
    seed_database(db)

    # Generate meal plan
    plan = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    assert plan.status_code == 201
    plan_id = plan.json()["id"]

    # Get grocery list
    grocery = client.get(f"/api/grocery/{plan_id}", headers=headers)
    assert grocery.status_code == 200
    assert len(grocery.json()["items"]) > 0

    # Log a dish
    recipe_id = plan.json()["days"][0]["breakfast"]
    log = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Great!",
        "would_make_again": True,
    }, headers=headers)
    assert log.status_code == 201
```

**Step 2: Run all tests**

Run: `cd backend && python -m pytest -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git commit -m "test: add end-to-end integration test for full user workflow"
```

---

### Task 23: GitHub Repository Setup

**Step 1: Create GitHub repo**

Run:
```bash
gh repo create diet-driven-health --public --source=. --remote=origin --push
```

**Step 2: Verify push succeeded**

Run: `git log --oneline`

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| Phase 1 | 1-9 | Backend: scaffolding, auth, profile, recipes, seed data, dish log, meal plans, grocery, parser |
| Phase 2 | 10-18 | Frontend: scaffolding, login, dashboard, recipes, meal plans, grocery, history, profile, upload |
| Phase 3 | 19-21 | Claude Code skills: recipe analyzer, profile builder, meal plan optimizer |
| Phase 4 | 22-23 | Integration testing and GitHub setup |
