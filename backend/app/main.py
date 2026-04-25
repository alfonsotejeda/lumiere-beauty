from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import connect_db, close_db
from app.cache import connect_cache, close_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await connect_cache()
    yield
    await close_db()
    await close_cache()

app = FastAPI(title="Lumière Beauty API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}
