from fastapi import APIRouter, HTTPException
import structlog
from app.schemas.gate import GateDecisionRequest, GateResponse
from app.database import get_supabase

log = structlog.get_logger()
router = APIRouter()


@router.get("/{gate_id}", response_model=GateResponse)
async def get_gate(gate_id: str) -> dict:
    db = get_supabase()

    # gate_id can be "gate1:{job_id}" or just "gate1" when looking up by job
    parts = gate_id.split(":")
    gate_name = parts[0]

    query = db.table("gates").select("*").eq("gate_id", gate_name)
    if len(parts) > 1:
        query = query.eq("job_id", parts[1])

    row = query.limit(1).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Gate not found")

    g = row.data[0]
    synthesis = db.table("audit_results").select("data_json").eq("job_id", g["job_id"]).eq("stream", "synthesis").execute()
    synthesis_data = synthesis.data[0]["data_json"] if synthesis.data else {}

    return {
        "id": str(g["id"]),
        "gate_id": g["gate_id"],
        "status": g["status"],
        "decision": g.get("decision"),
        "comment": g.get("comment"),
        "synthesis": synthesis_data,
    }


@router.post("/{gate_id}/approve")
async def approve_gate(gate_id: str, request: GateDecisionRequest) -> dict:
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

    log.info("gate.approved", gate_id=gate_name, job_id=job_id)
    return {"status": "approved", "gate_id": gate_name, "job_id": job_id}


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
