from fastapi import APIRouter
from app.schemas.job import CreateJobRequest, JobResponse
from app.database import get_supabase

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(request: CreateJobRequest) -> dict:
    # TODO: persist job to Supabase, dispatch audit agents via orchestrator
    raise NotImplementedError


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> dict:
    # TODO: fetch from Supabase jobs table
    raise NotImplementedError


@router.get("/", response_model=list[JobResponse])
async def list_jobs() -> list:
    # TODO: fetch all jobs for authenticated user
    raise NotImplementedError
