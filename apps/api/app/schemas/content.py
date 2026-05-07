from pydantic import BaseModel


class SaveDraftRequest(BaseModel):
    body: str


class DraftResponse(BaseModel):
    id: str
    status: str
    body: str
    updated_at: str
