from datetime import datetime
from uuid import UUID

from domain.call_link import CallLink
from domain.repositories import SessionRepository, CallLinkRepository
from domain.session import ProxySession, SessionStatus
from infrastructure.proxy.process_manager import process_manager


class CallLinkNotFound(Exception):
    pass


class SessionError(Exception):
    pass


async def create_session(
    user_id: UUID,
    call_link_id: UUID,
    listen_port: int,
    peer_addr: str,
    session_repo: SessionRepository,
    call_link_repo: CallLinkRepository,
) -> ProxySession:
    link = await call_link_repo.get_by_id(call_link_id)
    if not link or link.user_id != user_id:
        raise CallLinkNotFound("Call link not found")

    # Allocate port if not specified or validate
    if listen_port == 0:
        listen_port = process_manager.allocate_port()
    else:
        # Try to use specified port
        if listen_port in process_manager._port_pool:
            process_manager._port_pool.discard(listen_port)

    session = ProxySession(
        user_id=user_id,
        call_link_id=call_link_id,
        listen_port=listen_port,
        peer_addr=peer_addr,
        status=SessionStatus.PENDING,
        started_at=datetime.utcnow(),
    )
    session = await session_repo.create(session)

    try:
        pid = await process_manager.start(session)
        session.pid = pid
        session.status = SessionStatus.ACTIVE
        session = await session_repo.update(session)
    except Exception as e:
        session.status = SessionStatus.FAILED
        await session_repo.update(session)
        raise SessionError(f"Failed to start proxy: {e}") from e

    # Update call link last_used_at
    link.last_used_at = datetime.utcnow()
    await call_link_repo.update(link)

    return session
