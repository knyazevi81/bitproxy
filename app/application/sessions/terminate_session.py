from datetime import datetime
from uuid import UUID

from domain.repositories import SessionRepository
from domain.session import SessionStatus
from infrastructure.proxy.process_manager import process_manager


class SessionNotFound(Exception):
    pass


class Forbidden(Exception):
    pass


async def terminate_session(
    session_id: UUID,
    user_id: UUID,
    session_repo: SessionRepository,
) -> None:
    session = await session_repo.get_by_id(session_id)
    if not session:
        raise SessionNotFound("Session not found")
    if session.user_id != user_id:
        raise Forbidden("Not your session")

    await process_manager.stop(session_id)

    session.status = SessionStatus.TERMINATED
    session.terminated_at = datetime.utcnow()
    await session_repo.update(session)
