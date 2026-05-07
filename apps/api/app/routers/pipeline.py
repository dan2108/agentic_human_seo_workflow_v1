from fastapi import APIRouter

router = APIRouter()


@router.get("/{job_id}/status")
async def get_pipeline_status(job_id: str) -> dict:
    # TODO: fetch all job_steps for job, return status map
    raise NotImplementedError
