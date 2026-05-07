from fastapi import APIRouter

router = APIRouter()


@router.get("/{job_id}")
async def get_aftercare_reports(job_id: str) -> list:
    # TODO: fetch all aftercare_reports for job ordered by checkpoint
    raise NotImplementedError
