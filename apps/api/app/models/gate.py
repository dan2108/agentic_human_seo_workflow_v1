from pydantic import BaseModel
from datetime import datetime


class Gate(BaseModel):
    id: str
    job_id: str
    gate_id: str  # gate1 | gate2 | gate3 | gate4
    status: str   # pending | approved | rejected
    reviewer_id: str | None = None
    decision: str | None = None
    comment: str | None = None
    decided_at: datetime | None = None
