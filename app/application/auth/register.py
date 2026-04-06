from domain.repositories import UserRepository
from domain.user import User
from infrastructure.security import hash_password


class UserAlreadyExists(Exception):
    pass


async def register_user(username: str, password: str, repo: UserRepository) -> User:
    existing = await repo.get_by_username(username)
    if existing:
        raise UserAlreadyExists(f"User '{username}' already exists")
    user = User(username=username, hashed_password=hash_password(password))
    return await repo.create(user)
