from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SessionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    TERMINATED = "terminated"
    FAILED = "failed"


@dataclass
class ProxySession:
    user_id: UUID
    call_link_id: UUID
    listen_port: int
    peer_addr: str
    id: UUID = field(default_factory=uuid4)
    status: SessionStatus = SessionStatus.PENDING
    pid: Optional[int] = None
    started_at: Optional[datetime] = None
    terminated_at: Optional[datetime] = None
    bytes_sent: int = 0
    bytes_received: int = 0
    last_seen_at: Optional[datetime] = None
