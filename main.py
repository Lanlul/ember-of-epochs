from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import game

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="LLM-driven text RPG with Big Pickle image generation",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")
app.mount(
    "/images",
    StaticFiles(directory=settings.image_output_dir),
    name="images",
)

app.include_router(game.router, prefix="/api", tags=["game"])
