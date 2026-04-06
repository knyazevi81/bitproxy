from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.repositories import UserRepository
from domain.user import User
from infrastructure.database.models import UserModel


def _to_domain(model: UserModel) -> User:
    u = User(username=model.username, hashed_password=model.hashed_password)
    u.id = model.id
    u.is_admin = model.is_admin
    u.is_active = model.is_active
    u.created_at = model.created_at
    return u


def _to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        username=user.username,
        hashed_password=user.hashed_password,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
    )


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self._session.execute(select(UserModel).where(UserModel.username == username))
        model = result.scalar_one_or_none()
        return _to_domain(model) if model else None

    async def create(self, user: User) -> User:
        model = _to_model(user)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)

    async def update(self, user: User) -> User:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user.id))
        model = result.scalar_one()
        model.username = user.username
        model.hashed_password = user.hashed_password
        model.is_admin = user.is_admin
        model.is_active = user.is_active
        await self._session.commit()
        await self._session.refresh(model)
        return _to_domain(model)
