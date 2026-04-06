from fastapi import APIRouter

from application.sessions.get_session_stats import get_stats_summary, get_sessions_history
from presentation.dependencies import CurrentUser, DbDep, get_session_repo

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
async def stats_summary(current_user: CurrentUser, db: DbDep):
    return await get_stats_summary(current_user.id, get_session_repo(db))


@router.get("/sessions-history")
async def sessions_history(current_user: CurrentUser, db: DbDep):
    return await get_sessions_history(current_user.id, get_session_repo(db))
