from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user import User
from infrastructure.database.session import get_async_session
from infrastructure.database.repositories.user_repository import SqlUserRepository
from infrastructure.database.repositories.refresh_token_repository import SqlRefreshTokenRepository
from infrastructure.database.repositories.session_repository import SqlSessionRepository
from infrastructure.database.repositories.call_link_repository import SqlCallLinkRepository
from infrastructure.security import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    async for session in get_async_session():
        yield session


DbDep = Annotated[AsyncSession, Depends(get_db)]


def get_user_repo(db: DbDep):
    return SqlUserRepository(db)


def get_token_repo(db: DbDep):
    return SqlRefreshTokenRepository(db)


def get_session_repo(db: DbDep):
    return SqlSessionRepository(db)


def get_call_link_repo(db: DbDep):
    return SqlCallLinkRepository(db)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbDep,
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    repo = SqlUserRepository(db)
    user = await repo.get_by_id(UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
