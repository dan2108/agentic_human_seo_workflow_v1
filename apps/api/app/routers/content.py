from fastapi import APIRouter
from app.schemas.content import SaveDraftRequest, DraftResponse
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str) -> dict:
    raise NotImplementedError


@router.patch("/{draft_id}", response_model=DraftResponse)
async def save_draft(draft_id: str, request: SaveDraftRequest) -> dict:
    # TODO: upsert body to Supabase content_drafts; auto-save on inactivity
    raise NotImplementedError


@router.post("/{draft_id}/copilot")
async def copilot_stream(draft_id: str, prompt: str) -> StreamingResponse:
    # TODO: stream Claude API response via SSE for TipTap co-pilot panel
    raise NotImplementedError
