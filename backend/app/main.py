from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.recipes import router as recipes_router
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

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(recipes_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
