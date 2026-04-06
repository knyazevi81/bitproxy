from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials

from application.auth.login import login_user, InvalidCredentials
from application.auth.refresh_token import refresh_access_token, InvalidToken
from application.auth.register import register_user, UserAlreadyExists
from presentation.dependencies import CurrentUser, DbDep, get_user_repo, get_token_repo
from presentation.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, response: Response, db: DbDep):
    user_repo = get_user_repo(db)
    token_repo = get_token_repo(db)
    try:
        user = await register_user(body.username, body.password, user_repo)
    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    access_token, refresh_token = await login_user(body.username, body.password, user_repo, token_repo)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, response: Response, db: DbDep):
    user_repo = get_user_repo(db)
    token_repo = get_token_repo(db)
    try:
        access_token, refresh_token = await login_user(body.username, body.password, user_repo, token_repo)
    except InvalidCredentials as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, response: Response, db: DbDep):
    user_repo = get_user_repo(db)
    token_repo = get_token_repo(db)
    try:
        access_token, new_refresh = await refresh_access_token(body.refresh_token, user_repo, token_repo)
    except InvalidToken as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
    )
    return TokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshRequest, response: Response, db: DbDep, current_user: CurrentUser):
    from infrastructure.security import hash_token
    token_repo = get_token_repo(db)
    await token_repo.revoke(hash_token(body.refresh_token))
    response.delete_cookie("refresh_token")


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_admin=current_user.is_admin,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
