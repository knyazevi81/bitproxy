from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateCallLinkRequest(BaseModel):
    raw_link: str
    label: str


class CallLinkResponse(BaseModel):
    id: UUID
    user_id: UUID
    raw_link: str
    label: str
    is_active: bool
    last_used_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TestCallLinkResponse(BaseModel):
    valid: bool
    message: str
