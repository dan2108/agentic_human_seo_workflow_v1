import json
from typing import AsyncIterator, Any
import anthropic
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import structlog

from app.database import get_supabase
from app.schemas.content import SaveDraftRequest, DraftResponse

log = structlog.get_logger()
router = APIRouter()


def _row_to_draft(d: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(d["id"]),
        "job_id": str(d["job_id"]),
        "status": d.get("status", "draft"),
        "body": d.get("body", ""),
        "brief": d.get("brief_json") or {},
        "outline": d.get("outline_json") or {},
        "updated_at": str(d.get("updated_at", "")),
    }


@router.post("/", response_model=DraftResponse)
async def create_draft(job_id: str) -> dict:
    db = get_supabase()
    row = db.table("content_drafts").insert({
        "job_id": job_id,
        "brief_json": {},
        "outline_json": {},
        "body": "",
        "status": "draft",
    }).execute()
    if not row.data:
        raise HTTPException(status_code=500, detail="Failed to create draft")
    return _row_to_draft(row.data[0])


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str) -> dict:
    db = get_supabase()
    row = db.table("content_drafts").select("*").eq("id", draft_id).limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Draft not found")
    return _row_to_draft(row.data[0])


@router.patch("/{draft_id}", response_model=DraftResponse)
async def save_draft(draft_id: str, request: SaveDraftRequest) -> dict:
    db = get_supabase()
    row = db.table("content_drafts").update({"body": request.body}).eq("id", draft_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Draft not found")
    return _row_to_draft(row.data[0])


async def _stream_copilot(prompt: str) -> AsyncIterator[str]:
    import os
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {json.dumps({'text': text})}\n\n"
    yield "data: [DONE]\n\n"


@router.get("/{draft_id}/copilot")
async def copilot_stream(draft_id: str, prompt: str = "") -> StreamingResponse:
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    db = get_supabase()
    row = db.table("content_drafts").select("body").eq("id", draft_id).limit(1).execute()
    body = row.data[0].get("body", "") if row.data else ""

    full_prompt = (
        "You are an expert SEO content editor and writing assistant. "
        f"Here is the current draft:\n\n{body[:2000]}\n\n"
        f"User request: {prompt}"
    )

    return StreamingResponse(
        _stream_copilot(full_prompt),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
