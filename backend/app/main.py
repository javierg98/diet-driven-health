from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.recipes import router as recipes_router
from app.api.dish_log import router as dish_log_router
from app.api.meal_plans import router as meal_plans_router
from app.api.grocery import router as grocery_router
from app.api.upload import router as upload_router
from app.api.food_submission import router as food_router
from app.database import Base, SessionLocal, engine
from app.models.food_entry import FoodEntry  # noqa: F401
from app.models.food_preference import FoodPreference  # noqa: F401
from app.services.seed import seed_database

app = FastAPI(title="Diet Driven Health", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(recipes_router)
app.include_router(dish_log_router)
app.include_router(meal_plans_router)
app.include_router(grocery_router)
app.include_router(upload_router)
app.include_router(food_router)


@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "healthy"}
