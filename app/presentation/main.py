import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.database.session import async_session_factory
from infrastructure.database.repositories.session_repository import SqlSessionRepository
from presentation.routers import auth, sessions, call_links, stats
from presentation.background import healthcheck_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_factory() as db:
        repo = SqlSessionRepository(db)
        await repo.mark_all_active_as_failed()
    asyncio.create_task(healthcheck_loop())
    yield


app = FastAPI(title="BitProxy API", version="1.0.0", lifespan=lifespan)

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


@app.get("/health")
async def health():
    return {"status": "ok"}
