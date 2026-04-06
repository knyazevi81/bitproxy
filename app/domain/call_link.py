from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class CallLink:
    user_id: UUID
    raw_link: str
    label: str
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    last_used_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
