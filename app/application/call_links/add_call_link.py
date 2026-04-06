from uuid import UUID

from domain.call_link import CallLink
from domain.repositories import CallLinkRepository
from infrastructure.vk_api.credentials import validate_call_link


class InvalidCallLink(Exception):
    pass


async def add_call_link(
    user_id: UUID,
    raw_link: str,
    label: str,
    call_link_repo: CallLinkRepository,
) -> CallLink:
    if not await validate_call_link(raw_link):
        raise InvalidCallLink("Invalid VK call link")
    link = CallLink(user_id=user_id, raw_link=raw_link, label=label)
    return await call_link_repo.create(link)
