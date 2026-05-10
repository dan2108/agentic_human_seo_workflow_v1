"""Content orchestrator — kicks off brief + outline after Gate 2 approval.

Fires when the human approves the strategy/calendar from Gate 2.
Generates a content brief and outline for the top-priority calendar entry,
then marks Gate 3 as awaiting human review (the writer opens the editor).
"""
from typing import Any
import structlog

from app.agents.content.brief_agent import BriefAgent
from app.agents.content.outline_agent import OutlineAgent

log = structlog.get_logger()


class ContentOrchestrator:
    def __init__(self, db: Any, settings: Any) -> None:
        self._db = db
        self._settings = settings

    def _set_step_status(self, job_id: str, step_id: str, status: str) -> None:
        self._db.table("job_steps").upsert(
            {"job_id": job_id, "step_id": step_id, "status": status}
        ).execute()

    async def dispatch(self, job_id: str, site_url: str) -> None:
        log.info("content_orchestrator.dispatch", job_id=job_id)
        s = self._settings

        try:
            self._set_step_status(job_id, "brief", "running")
            await BriefAgent(self._db, anthropic_api_key=s.anthropic_api_key).run(job_id, site_url)
            self._set_step_status(job_id, "brief", "complete")
        except Exception as exc:
            log.error("brief_agent.failed", job_id=job_id, error=str(exc))
            self._set_step_status(job_id, "brief", "failed")
            return

        try:
            self._set_step_status(job_id, "outline", "running")
            await OutlineAgent(self._db, anthropic_api_key=s.anthropic_api_key).run(job_id, site_url)
            self._set_step_status(job_id, "outline", "complete")
        except Exception as exc:
            log.error("outline_agent.failed", job_id=job_id, error=str(exc))
            self._set_step_status(job_id, "outline", "failed")
            return

        # Gate 3 — writer opens the editor; QA agents run on demand from there.
        self._db.table("gates").upsert(
            {"job_id": job_id, "gate_id": "gate3", "status": "pending"}
        ).execute()
        self._set_step_status(job_id, "gate-3", "awaiting_human")
        log.info("content_orchestrator.complete", job_id=job_id)
