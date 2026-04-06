import asyncio
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from presentation.routers import auth, sessions, call_links, stats
from presentation.background import healthcheck_loop

app = FastAPI(title="BitProxy API", version="1.0.0")

# CORS
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(call_links.router)
app.include_router(stats.router)


@app.on_event("startup")
async def startup():
    asyncio.create_task(healthcheck_loop())


@app.get("/health")
async def health():
    return {"status": "ok"}
