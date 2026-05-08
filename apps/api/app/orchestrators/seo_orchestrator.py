import asyncio
from typing import Any
import structlog
from app.agents.audit.crawl_agent import CrawlAgent
from app.agents.audit.technical_agent import TechnicalAgent
from app.agents.audit.onpage_agent import OnPageAgent
from app.agents.audit.content_audit_agent import ContentAuditAgent
from app.agents.audit.authority_agent import AuthorityAgent
from app.agents.audit.competitive_agent import CompetitiveAgent
from app.agents.audit.analytics_agent import AnalyticsAgent
from app.agents.synthesis_agent import SynthesisAgent

log = structlog.get_logger()

AUDIT_STEPS = [
    "pre-check", "crawl", "technical", "onpage",
    "content", "authority", "competitive", "analytics", "synthesis",
]


class SEOOrchestrator:
    def __init__(self, db: Any, settings: Any) -> None:
        self._db = db
        self._settings = settings

    def _set_step_status(self, job_id: str, step_id: str, status: str) -> None:
        self._db.table("job_steps").upsert(
            {"job_id": job_id, "step_id": step_id, "status": status}
        ).execute()

    async def dispatch(self, job_id: str, site_url: str) -> None:
        log.info("seo_orchestrator.dispatch", job_id=job_id)

        # Mark all audit steps as running
        for step in AUDIT_STEPS:
            self._set_step_status(job_id, step, "queued")

        # Update job status to running
        self._db.table("jobs").update({"status": "running"}).eq("id", job_id).execute()

        s = self._settings
        agents = [
            ("crawl", CrawlAgent(self._db)),
            ("technical", TechnicalAgent(self._db)),
            ("onpage", OnPageAgent(self._db)),
            ("content", ContentAuditAgent(self._db, anthropic_api_key=s.anthropic_api_key)),
            ("authority", AuthorityAgent(self._db, ahrefs_api_key=s.ahrefs_api_key)),
            ("competitive", CompetitiveAgent(self._db, dataforseo_login=s.dataforseo_login, dataforseo_password=s.dataforseo_password)),
            ("analytics", AnalyticsAgent(self._db)),
        ]

        async def _run_agent(step_id: str, agent: Any) -> None:
            try:
                self._set_step_status(job_id, step_id, "running")
                await agent.run(job_id, site_url)
                self._set_step_status(job_id, step_id, "complete")
            except Exception as exc:
                log.error("agent.failed", step_id=step_id, error=str(exc))
                self._set_step_status(job_id, step_id, "failed")

        await asyncio.gather(*[_run_agent(sid, ag) for sid, ag in agents])

        # Synthesis after all audit agents finish
        try:
            self._set_step_status(job_id, "synthesis", "running")
            synthesis = SynthesisAgent(self._db, anthropic_api_key=s.anthropic_api_key)
            await synthesis.run(job_id, site_url=site_url)
            self._set_step_status(job_id, "synthesis", "complete")
        except Exception as exc:
            log.error("synthesis.failed", error=str(exc))
            self._set_step_status(job_id, "synthesis", "failed")

        # Gate 1 — mark as awaiting_human
        self._db.table("gates").upsert(
            {"job_id": job_id, "gate_id": "gate1", "status": "pending"}
        ).execute()
        self._set_step_status(job_id, "gate-1", "awaiting_human")
        log.info("seo_orchestrator.audit_complete", job_id=job_id)
