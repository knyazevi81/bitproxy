from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from application.call_links.add_call_link import add_call_link, InvalidCallLink
from application.call_links.delete_call_link import delete_call_link, CallLinkNotFound, Forbidden
from application.call_links.list_call_links import list_call_links
from infrastructure.vk_api.credentials import validate_call_link
from presentation.dependencies import CurrentUser, DbDep, get_call_link_repo
from presentation.schemas.call_link import CallLinkResponse, CreateCallLinkRequest, TestCallLinkResponse

router = APIRouter(prefix="/api/call-links", tags=["call-links"])


def _to_response(link) -> CallLinkResponse:
    return CallLinkResponse(
        id=link.id,
        user_id=link.user_id,
        raw_link=link.raw_link,
        label=link.label,
        is_active=link.is_active,
        last_used_at=link.last_used_at,
        created_at=link.created_at,
    )


@router.get("/", response_model=list[CallLinkResponse])
async def get_call_links(current_user: CurrentUser, db: DbDep):
    links = await list_call_links(current_user.id, get_call_link_repo(db))
    return [_to_response(l) for l in links]


@router.post("/", response_model=CallLinkResponse, status_code=status.HTTP_201_CREATED)
async def post_call_link(body: CreateCallLinkRequest, current_user: CurrentUser, db: DbDep):
    try:
        link = await add_call_link(current_user.id, body.raw_link, body.label, get_call_link_repo(db))
    except InvalidCallLink as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return _to_response(link)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(link_id: UUID, current_user: CurrentUser, db: DbDep):
    try:
        await delete_call_link(link_id, current_user.id, get_call_link_repo(db))
    except CallLinkNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/{link_id}/test", response_model=TestCallLinkResponse)
async def test_call_link(link_id: UUID, current_user: CurrentUser, db: DbDep):
    link_repo = get_call_link_repo(db)
    link = await link_repo.get_by_id(link_id)
    if not link or link.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call link not found")
    valid = await validate_call_link(link.raw_link)
    return TestCallLinkResponse(
        valid=valid,
        message="Link appears valid" if valid else "Link validation failed",
    )
