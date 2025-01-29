# app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth
from app.routes import note
from app.routes import diary
from app.utils.database import init_db

# Create FastAPI instance
app = FastAPI(
    title="Migo Backend",
    description="Backend API for iOS Migo App",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Blueprints
app.include_router(auth.router, prefix="/auth")
app.include_router(note.router, prefix="/notes")
app.include_router(diary.router, prefix="/diaries")

@app.on_event("startup")
def startup_event():
    init_db()

