from supabase import Client
from app.database import get_supabase


class SupabaseService:
    def __init__(self):
        self.db: Client = get_supabase()

    async def update_step_status(self, job_id: str, step_id: str, status: str, output: dict | None = None) -> None:
        self.db.table("job_steps").upsert({"job_id": job_id, "step_id": step_id, "status": status, "output_json": output}).execute()
