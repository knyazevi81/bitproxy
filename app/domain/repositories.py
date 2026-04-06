from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.user import User
from domain.session import ProxySession, SessionStatus
from domain.call_link import CallLink


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        ...

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        ...

    @abstractmethod
    async def create(self, user: User) -> User:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def create(self, user_id: UUID, token_hash: str, expires_at) -> None:
        ...

    @abstractmethod
    async def get_by_hash(self, token_hash: str):
        ...

    @abstractmethod
    async def revoke(self, token_hash: str) -> None:
        ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> None:
        ...


class SessionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[ProxySession]:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[ProxySession]:
        ...

    @abstractmethod
    async def list_active(self, user_id: UUID) -> list[ProxySession]:
        ...

    @abstractmethod
    async def list_all_active(self) -> list[ProxySession]:
        ...

    @abstractmethod
    async def create(self, session: ProxySession) -> ProxySession:
        ...

    @abstractmethod
    async def update(self, session: ProxySession) -> ProxySession:
        ...

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        ...


class CallLinkRepository(ABC):
    @abstractmethod
    async def get_by_id(self, link_id: UUID) -> Optional[CallLink]:
        ...

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[CallLink]:
        ...

    @abstractmethod
    async def create(self, link: CallLink) -> CallLink:
        ...

    @abstractmethod
    async def update(self, link: CallLink) -> CallLink:
        ...

    @abstractmethod
    async def delete(self, link_id: UUID) -> None:
        ...
