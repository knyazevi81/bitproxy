from uuid import UUID

from domain.repositories import CallLinkRepository


class CallLinkNotFound(Exception):
    pass


class Forbidden(Exception):
    pass


async def delete_call_link(
    link_id: UUID,
    user_id: UUID,
    call_link_repo: CallLinkRepository,
) -> None:
    link = await call_link_repo.get_by_id(link_id)
    if not link:
        raise CallLinkNotFound("Call link not found")
    if link.user_id != user_id:
        raise Forbidden("Not your call link")
    await call_link_repo.delete(link_id)
