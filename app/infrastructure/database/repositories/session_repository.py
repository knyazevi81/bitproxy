from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories import SessionRepository
from domain.session import ProxySession, SessionStatus
from infrastructure.database.models import SessionModel


def _to_domain(model: SessionModel) -> ProxySession:
    s = ProxySession(
        user_id=model.user_id,
        call_link_id=model.call_link_id,
        listen_port=model.listen_port,
        peer_addr=model.peer_addr,
    )
    s.id = model.id
    s.status = SessionStatus(model.status)
    s.pid = model.pid
    s.started_at = model.started_at
    s.terminated_at = model.terminated_at
    s.bytes_sent = model.bytes_sent
    s.bytes_received = model.bytes_received
    s.last_seen_at = model.last_seen_at
    return s


def _apply_to_model(model: SessionModel, session: ProxySession) -> None:
    model.status = session.status.value
    model.pid = session.pid
    model.started_at = session.started_at
    model.terminated_at = session.terminated_at
    model.bytes_sent = session.bytes_sent
    model.bytes_received = session.bytes_received
    model.last_seen_at = session.last_seen_at
    model.listen_port = session.listen_port
    model.peer_addr = session.peer_addr


class SqlSessionRepository(SessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, session_id: UUID) -> Optional[ProxySession]:
        result = await self._session.execute(select(SessionModel).where(SessionModel.id == session_id))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[ProxySession]:
        result = await self._session.execute(
            select(SessionModel).where(SessionModel.user_id == user_id).order_by(SessionModel.started_at.desc())
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def list_active(self, user_id: UUID) -> list[ProxySession]:
        result = await self._session.execute(
            select(SessionModel).where(
                SessionModel.user_id == user_id,
                SessionModel.status.in_([SessionStatus.ACTIVE.value, SessionStatus.PENDING.value]),
            )
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def list_all_active(self) -> list[ProxySession]:
        result = await self._session.execute(
            select(SessionModel).where(
                SessionModel.status.in_([SessionStatus.ACTIVE.value, SessionStatus.PENDING.value])
            )
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def create(self, session: ProxySession) -> ProxySession:
        model = SessionModel(
            id=session.id,
            user_id=session.user_id,
            call_link_id=session.call_link_id,
            listen_port=session.listen_port,
            peer_addr=session.peer_addr,
            status=session.status.value,
            pid=session.pid,
            started_at=session.started_at,
            terminated_at=session.terminated_at,
            bytes_sent=session.bytes_sent,
            bytes_received=session.bytes_received,
            last_seen_at=session.last_seen_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def update(self, session: ProxySession) -> ProxySession:
        result = await self._session.execute(select(SessionModel).where(SessionModel.id == session.id))
        model = result.scalar_one()
        _apply_to_model(model, session)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def mark_all_active_as_failed(self) -> None:
        await self._session.execute(
            update(SessionModel)
            .where(SessionModel.status.in_([SessionStatus.PENDING.value, SessionStatus.ACTIVE.value]))
            .values(status=SessionStatus.FAILED.value, terminated_at=datetime.now(timezone.utc))
        )
        await self._session.commit()

    async def delete(self, session_id: UUID) -> None:
        result = await self._session.execute(select(SessionModel).where(SessionModel.id == session_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
