from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.call_link import CallLink
from domain.repositories import CallLinkRepository
from infrastructure.database.models import CallLinkModel


def _to_domain(model: CallLinkModel) -> CallLink:
    link = CallLink(user_id=model.user_id, raw_link=model.raw_link, label=model.label)
    link.id = model.id
    link.is_active = model.is_active
    link.last_used_at = model.last_used_at
    link.created_at = model.created_at
    return link


class SqlCallLinkRepository(CallLinkRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, link_id: UUID) -> Optional[CallLink]:
        result = await self._session.execute(select(CallLinkModel).where(CallLinkModel.id == link_id))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[CallLink]:
        result = await self._session.execute(
            select(CallLinkModel)
            .where(CallLinkModel.user_id == user_id)
            .order_by(CallLinkModel.created_at.desc())
        )
        return [_to_domain(m) for m in result.scalars().all()]

    async def create(self, link: CallLink) -> CallLink:
        model = CallLinkModel(
            id=link.id,
            user_id=link.user_id,
            raw_link=link.raw_link,
            label=link.label,
            is_active=link.is_active,
            last_used_at=link.last_used_at,
            created_at=link.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def update(self, link: CallLink) -> CallLink:
        result = await self._session.execute(select(CallLinkModel).where(CallLinkModel.id == link.id))
        model = result.scalar_one()
        model.raw_link = link.raw_link
        model.label = link.label
        model.is_active = link.is_active
        model.last_used_at = link.last_used_at
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def delete(self, link_id: UUID) -> None:
        result = await self._session.execute(select(CallLinkModel).where(CallLinkModel.id == link_id))
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
