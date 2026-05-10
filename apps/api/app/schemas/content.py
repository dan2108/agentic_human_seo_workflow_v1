from pydantic import BaseModel
from typing import Any


class SaveDraftRequest(BaseModel):
    body: str


class DraftResponse(BaseModel):
    id: str
    job_id: str
    status: str
    body: str
    brief: dict[str, Any] = {}
    outline: dict[str, Any] = {}
    updated_at: str
