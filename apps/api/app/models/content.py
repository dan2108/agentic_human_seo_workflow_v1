from pydantic import BaseModel
from datetime import datetime


class ContentDraft(BaseModel):
    id: str
    job_id: str
    brief_json: dict
    outline_json: dict
    body: str
    status: str  # draft | qa_pending | approved | published
    created_at: datetime
    updated_at: datetime
