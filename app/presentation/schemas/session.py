from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from domain.session import SessionStatus


class CreateSessionRequest(BaseModel):
    call_link_id: UUID
    listen_port: int = 0
    peer_addr: str = "127.0.0.1:51820"
    streams_count: int = 8
    use_udp: bool = False


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    call_link_id: UUID
    status: SessionStatus
    listen_port: int
    peer_addr: str
    pid: Optional[int]
    started_at: Optional[datetime]
    terminated_at: Optional[datetime]
    bytes_sent: int
    bytes_received: int
    last_seen_at: Optional[datetime]

    model_config = {"from_attributes": True}


class SessionLogsResponse(BaseModel):
    session_id: UUID
    lines: list[str]
