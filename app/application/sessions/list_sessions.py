from uuid import UUID

from domain.repositories import SessionRepository
from domain.session import ProxySession


async def list_sessions(user_id: UUID, session_repo: SessionRepository) -> list[ProxySession]:
    return await session_repo.list_by_user(user_id)


async def list_active_sessions(user_id: UUID, session_repo: SessionRepository) -> list[ProxySession]:
    return await session_repo.list_active(user_id)
