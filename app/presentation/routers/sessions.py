from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from application.sessions.create_session import create_session, CallLinkNotFound, SessionError
from application.sessions.terminate_session import terminate_session, SessionNotFound, Forbidden
from application.sessions.list_sessions import list_sessions, list_active_sessions
from domain.session import SessionStatus
from infrastructure.proxy.process_manager import process_manager
from presentation.dependencies import CurrentUser, DbDep, get_session_repo, get_call_link_repo
from presentation.schemas.session import CreateSessionRequest, SessionResponse, SessionLogsResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _session_to_response(s) -> SessionResponse:
    return SessionResponse(
        id=s.id,
        user_id=s.user_id,
        call_link_id=s.call_link_id,
        status=s.status,
        listen_port=s.listen_port,
        peer_addr=s.peer_addr,
        pid=s.pid,
        started_at=s.started_at,
        terminated_at=s.terminated_at,
        bytes_sent=s.bytes_sent,
        bytes_received=s.bytes_received,
        last_seen_at=s.last_seen_at,
    )


@router.get("/active", response_model=list[SessionResponse])
async def get_active_sessions(current_user: CurrentUser, db: DbDep):
    sessions = await list_active_sessions(current_user.id, get_session_repo(db))
    return [_session_to_response(s) for s in sessions]


@router.get("/", response_model=list[SessionResponse])
async def get_sessions(current_user: CurrentUser, db: DbDep):
    sessions = await list_sessions(current_user.id, get_session_repo(db))
    return [_session_to_response(s) for s in sessions]


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def post_session(body: CreateSessionRequest, current_user: CurrentUser, db: DbDep):
    session_repo = get_session_repo(db)
    call_link_repo = get_call_link_repo(db)
    try:
        session = await create_session(
            user_id=current_user.id,
            call_link_id=body.call_link_id,
            listen_port=body.listen_port,
            peer_addr=body.peer_addr,
            session_repo=session_repo,
            call_link_repo=call_link_repo,
        )
    except CallLinkNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except SessionError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return _session_to_response(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, current_user: CurrentUser, db: DbDep):
    session_repo = get_session_repo(db)
    session = await session_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return _session_to_response(session)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: UUID, current_user: CurrentUser, db: DbDep):
    session_repo = get_session_repo(db)
    try:
        await terminate_session(session_id, current_user.id, session_repo)
    except SessionNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Forbidden as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/{session_id}/logs", response_model=SessionLogsResponse)
async def get_session_logs(session_id: UUID, current_user: CurrentUser, db: DbDep, lines: int = 50):
    session_repo = get_session_repo(db)
    session = await session_repo.get_by_id(session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    log_lines = await process_manager.get_log_tail(session_id, lines)
    return SessionLogsResponse(session_id=session_id, lines=log_lines)
