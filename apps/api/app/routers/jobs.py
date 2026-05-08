import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, HTTPException
import structlog
from app.schemas.job import CreateJobRequest, JobResponse
from app.database import get_supabase
from app.config import settings

log = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=201)
async def create_job(request: CreateJobRequest, background_tasks: BackgroundTasks) -> dict:
    db = get_supabase()
    site_url = str(request.site_url)

    row = (
        db.table("jobs")
        .insert({
            "site_url": site_url,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        .execute()
    )
    job = row.data[0] if row.data else None
    if not job:
        raise HTTPException(status_code=500, detail="Failed to create job")

    job_id = job["id"]
    log.info("job.created", job_id=job_id, site_url=site_url)

    async def _run_audit() -> None:
        from app.orchestrators.seo_orchestrator import SEOOrchestrator
        orch = SEOOrchestrator(db, settings)
        await orch.dispatch(job_id, site_url)

    background_tasks.add_task(_run_audit)

    return {
        "id": str(job_id),
        "site_url": site_url,
        "status": "queued",
        "created_at": job.get("created_at", ""),
    }


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> dict:
    db = get_supabase()
    row = db.table("jobs").select("*").eq("id", job_id).execute()
    if not row.data:
        raise HTTPException(status_code=404, detail="Job not found")
    job = row.data[0]
    return {"id": str(job["id"]), "site_url": job["site_url"], "status": job["status"], "created_at": str(job["created_at"])}


@router.get("/", response_model=list[JobResponse])
async def list_jobs() -> list:
    db = get_supabase()
    rows = db.table("jobs").select("*").order("created_at", desc=True).limit(50).execute()
    return [
        {"id": str(j["id"]), "site_url": j["site_url"], "status": j["status"], "created_at": str(j["created_at"])}
        for j in (rows.data or [])
    ]
