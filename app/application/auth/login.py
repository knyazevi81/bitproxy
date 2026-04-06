from domain.repositories import UserRepository, RefreshTokenRepository
from domain.user import User
from infrastructure.security import verify_password, create_access_token, create_refresh_token


class InvalidCredentials(Exception):
    pass


async def login_user(
    username: str,
    password: str,
    user_repo: UserRepository,
    token_repo: RefreshTokenRepository,
) -> tuple[str, str]:
    """Returns (access_token, refresh_token)."""
    user = await user_repo.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        raise InvalidCredentials("Invalid username or password")
    if not user.is_active:
        raise InvalidCredentials("Account is disabled")

    access_token = create_access_token(str(user.id))
    refresh_token, token_hash, expires_at = create_refresh_token(str(user.id))
    await token_repo.create(user.id, token_hash, expires_at)
    return access_token, refresh_token
