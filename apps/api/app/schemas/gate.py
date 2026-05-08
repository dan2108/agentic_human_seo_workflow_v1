from typing import Any
from pydantic import BaseModel


class GateDecisionRequest(BaseModel):
    comment: str | None = None


class GateResponse(BaseModel):
    id: str
    gate_id: str
    status: str
    decision: str | None = None
    comment: str | None = None
    synthesis: dict[str, Any] = {}
