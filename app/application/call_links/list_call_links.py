from uuid import UUID

from domain.call_link import CallLink
from domain.repositories import CallLinkRepository


async def list_call_links(user_id: UUID, call_link_repo: CallLinkRepository) -> list[CallLink]:
    return await call_link_repo.list_by_user(user_id)
