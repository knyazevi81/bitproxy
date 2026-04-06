from domain.repositories import UserRepository, RefreshTokenRepository
from infrastructure.security import (
    verify_refresh_token,
    create_access_token,
    create_refresh_token,
    hash_token,
)


class InvalidToken(Exception):
    pass


async def refresh_access_token(
    refresh_token: str,
    user_repo: UserRepository,
    token_repo: RefreshTokenRepository,
) -> tuple[str, str]:
    """Returns (new_access_token, new_refresh_token)."""
    payload = verify_refresh_token(refresh_token)
    if not payload:
        raise InvalidToken("Invalid or expired refresh token")

    token_hash = hash_token(refresh_token)
    stored = await token_repo.get_by_hash(token_hash)
    if not stored:
        raise InvalidToken("Token not found or revoked")

    user_id = payload["sub"]
    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise InvalidToken("User not found or inactive")

    # Rotate: revoke old, issue new
    await token_repo.revoke(token_hash)
    new_access = create_access_token(user_id)
    new_refresh, new_hash, new_expires = create_refresh_token(user_id)
    await token_repo.create(user.id, new_hash, new_expires)
    return new_access, new_refresh
