from pydantic import BaseModel
from datetime import datetime


class Job(BaseModel):
    id: str
    site_url: str
    status: str  # queued | running | awaiting_human | complete | failed
    created_at: datetime
    updated_at: datetime


class JobStep(BaseModel):
    id: str
    job_id: str
    step_id: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    output_json: dict | None = None
