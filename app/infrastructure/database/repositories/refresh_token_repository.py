from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories import RefreshTokenRepository
from infrastructure.database.models import RefreshTokenModel


class SqlRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user_id: UUID, token_hash: str, expires_at: datetime) -> None:
        model = RefreshTokenModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self._session.add(model)
        await self._session.commit()

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshTokenModel]:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.revoked == False,
                RefreshTokenModel.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_hash: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.token_hash == token_hash)
            .values(revoked=True)
        )
        await self._session.commit()

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .values(revoked=True)
        )
        await self._session.commit()
