from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
import structlog

from app.schemas.gate import GateDecisionRequest, GateResponse
from app.database import get_supabase
from app.config import settings

log = structlog.get_logger()
router = APIRouter()

GATE_STREAMS: dict[str, list[str]] = {
    "gate1": ["synthesis"],
    "gate2": ["calendar", "clusters", "intent"],
    "gate3": ["editor_review", "fact_check", "voice_check", "plagiarism"],
    "gate4": ["publish_result", "linking", "distribution"],
}


def _fetch_streams(db, job_id: str, streams: list[str]) -> dict:
    if len(streams) == 1:
        row = db.table("audit_results").select("data_json").eq("job_id", job_id).eq("stream", streams[0]).execute()
        return row.data[0]["data_json"] if row.data else {}
    result: dict = {}
    for stream in streams:
        row = db.table("audit_results").select("data_json").eq("job_id", job_id).eq("stream", stream).execute()
        if row.data:
            result[stream] = row.data[0]["data_json"]
    return result


def _fetch_site_url(db, job_id: str) -> str:
    row = db.table("jobs").select("site_url").eq("id", job_id).limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return row.data[0]["site_url"]


def _schedule_next_phase(
    background_tasks: BackgroundTasks,
    db: Any,
    gate_name: str,
    job_id: str,
) -> str | None:
    """Register the next-phase orchestrator as a background task.

    Returns the name of the dispatched orchestrator, or None for terminal gates.
    Failures inside the background task are logged but do NOT roll back the
    gate approval — the human decision stands; the agent step marks failed.
    """
    if gate_name == "gate1":
        from app.orchestrators.research_orchestrator import ResearchOrchestrator
        site_url = _fetch_site_url(db, job_id)

        async def _run() -> None:
            try:
                orch = ResearchOrchestrator(
                    db,
                    dataforseo_login=settings.dataforseo_login,
                    dataforseo_password=settings.dataforseo_password,
                    anthropic_api_key=settings.anthropic_api_key,
                )
                await orch.dispatch(job_id, site_url)
            except Exception as exc:
                log.error("research_orchestrator.dispatch_failed", job_id=job_id, error=str(exc))

        background_tasks.add_task(_run)
        return "research_orchestrator"

    if gate_name == "gate2":
        from app.orchestrators.content_orchestrator import ContentOrchestrator
        site_url = _fetch_site_url(db, job_id)

        async def _run() -> None:
            try:
                await ContentOrchestrator(db, settings).dispatch(job_id, site_url)
            except Exception as exc:
                log.error("content_orchestrator.dispatch_failed", job_id=job_id, error=str(exc))

        background_tasks.add_task(_run)
        return "content_orchestrator"

    if gate_name == "gate3":
        from app.orchestrators.publish_orchestrator import PublishOrchestrator
        site_url = _fetch_site_url(db, job_id)

        async def _run() -> None:
            try:
                await PublishOrchestrator(db, settings).dispatch(job_id, site_url)
            except Exception as exc:
                log.error("publish_orchestrator.dispatch_failed", job_id=job_id, error=str(exc))

        background_tasks.add_task(_run)
        return "publish_orchestrator"

    if gate_name == "gate4":
        from app.orchestrators.aftercare_orchestrator import AftercareOrchestrator
        published_at = datetime.now(timezone.utc).isoformat()

        async def _run() -> None:
            try:
                await AftercareOrchestrator().schedule(job_id, published_at)
            except Exception as exc:
                log.error("aftercare_orchestrator.schedule_failed", job_id=job_id, error=str(exc))

        background_tasks.add_task(_run)
        return "aftercare_orchestrator"

    return None


@router.get("/{gate_id}", response_model=GateResponse)
async def get_gate(gate_id: str) -> dict:
    db = get_supabase()

    parts = gate_id.split(":")
    gate_name = parts[0]

    query = db.table("gates").select("*").eq("gate_id", gate_name)
    if len(parts) > 1:
        query = query.eq("job_id", parts[1])

    row = query.limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Gate not found")

    g = row.data[0]
    streams = GATE_STREAMS.get(gate_name, ["synthesis"])
    synthesis_data = _fetch_streams(db, g["job_id"], streams)

    return {
        "id": str(g["id"]),
        "gate_id": g["gate_id"],
        "status": g["status"],
        "decision": g.get("decision"),
        "comment": g.get("comment"),
        "synthesis": synthesis_data,
    }


@router.post("/{gate_id}/approve")
async def approve_gate(
    gate_id: str,
    request: GateDecisionRequest,
    background_tasks: BackgroundTasks,
) -> dict:
    db = get_supabase()
    parts = gate_id.split(":")
    gate_name, job_id = parts[0], parts[1] if len(parts) > 1 else None

    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required: use /gates/gate1:{job_id}/approve")

    db.table("gates").update({
        "status": "approved",
        "decision": "approved",
        "comment": request.comment,
    }).eq("gate_id", gate_name).eq("job_id", job_id).execute()

    db.table("job_steps").upsert({
        "job_id": job_id, "step_id": gate_name, "status": "complete"
    }).execute()

    next_orchestrator = _schedule_next_phase(background_tasks, db, gate_name, job_id)
    log.info("gate.approved", gate_id=gate_name, job_id=job_id, next=next_orchestrator)

    return {
        "status": "approved",
        "gate_id": gate_name,
        "job_id": job_id,
        "next": next_orchestrator,
    }


@router.post("/{gate_id}/reject")
async def reject_gate(gate_id: str, request: GateDecisionRequest) -> dict:
    db = get_supabase()
    parts = gate_id.split(":")
    gate_name, job_id = parts[0], parts[1] if len(parts) > 1 else None

    if not job_id:
        raise HTTPException(status_code=400, detail="job_id required: use /gates/gate1:{job_id}/reject")

    db.table("gates").update({
        "status": "rejected",
        "decision": "rejected",
        "comment": request.comment,
    }).eq("gate_id", gate_name).eq("job_id", job_id).execute()

    db.table("job_steps").upsert({
        "job_id": job_id, "step_id": gate_name, "status": "failed"
    }).execute()

    log.info("gate.rejected", gate_id=gate_name, job_id=job_id)
    return {"status": "rejected", "gate_id": gate_name, "job_id": job_id}
