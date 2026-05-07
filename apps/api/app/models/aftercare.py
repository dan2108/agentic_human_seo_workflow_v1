from pydantic import BaseModel
from datetime import datetime


class AftercareReport(BaseModel):
    id: str
    job_id: str
    checkpoint: str  # day7 | day30 | day90
    data_json: dict
    created_at: datetime


class BaselineSnapshot(BaseModel):
    id: str
    job_id: str
    url: str
    metrics_json: dict
    captured_at: datetime
