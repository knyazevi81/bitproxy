"""
Background task: every 30 seconds checks all active sessions and marks as FAILED
if the underlying process is no longer alive.
"""
import asyncio
from datetime import datetime

from domain.session import SessionStatus
from infrastructure.database.session import async_session_factory
from infrastructure.database.repositories.session_repository import SqlSessionRepository
from infrastructure.proxy.process_manager import process_manager


async def healthcheck_loop():
    while True:
        await asyncio.sleep(30)
        try:
            async with async_session_factory() as db:
                repo = SqlSessionRepository(db)
                active = await repo.list_all_active()
                for session in active:
                    alive = await process_manager.is_alive(session.id)
                    if not alive:
                        session.status = SessionStatus.FAILED
                        session.terminated_at = datetime.utcnow()
                        await repo.update(session)
        except Exception:
            pass  # don't crash the loop on transient errors
