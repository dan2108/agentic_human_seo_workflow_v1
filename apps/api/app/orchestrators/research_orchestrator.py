import asyncio
from typing import Any
import structlog

from app.agents.research.keyword_agent import KeywordAgent
from app.agents.research.serp_agent import SerpAgent
from app.agents.research.intent_agent import IntentAgent
from app.agents.research.cluster_agent import ClusterAgent
from app.agents.research.calendar_agent import CalendarAgent

log = structlog.get_logger()


class ResearchOrchestrator:
    def __init__(
        self,
        db: Any,
        dataforseo_login: str,
        dataforseo_password: str,
        anthropic_api_key: str,
    ) -> None:
        self._db = db
        self._dfs_login = dataforseo_login
        self._dfs_password = dataforseo_password
        self._anthropic_key = anthropic_api_key

    async def dispatch(self, job_id: str, site_url: str) -> None:
        log.info("research_orchestrator.dispatch", job_id=job_id)

        self._update_step(job_id, "keyword-research", "running")
        self._update_step(job_id, "serp-analysis", "running")

        keyword_agent = KeywordAgent(self._db, self._dfs_login, self._dfs_password)
        serp_agent = SerpAgent(self._db, self._dfs_login, self._dfs_password)
        await asyncio.gather(
            keyword_agent.run(job_id, site_url),
            serp_agent.run(job_id, site_url),
        )

        self._update_step(job_id, "keyword-research", "complete")
        self._update_step(job_id, "serp-analysis", "complete")

        self._update_step(job_id, "intent-classification", "running")
        self._update_step(job_id, "cluster-building", "running")

        intent_agent = IntentAgent(self._db, self._anthropic_key)
        cluster_agent = ClusterAgent(self._db, self._anthropic_key)
        await asyncio.gather(
            intent_agent.run(job_id, site_url),
            cluster_agent.run(job_id, site_url),
        )

        self._update_step(job_id, "intent-classification", "complete")
        self._update_step(job_id, "cluster-building", "complete")

        self._update_step(job_id, "content-calendar", "running")
        calendar_agent = CalendarAgent(self._db, self._anthropic_key)
        await calendar_agent.run(job_id, site_url)
        self._update_step(job_id, "content-calendar", "complete")

        self._update_step(job_id, "gate-2", "awaiting_human")
        log.info("research_orchestrator.complete", job_id=job_id)

    def _update_step(self, job_id: str, step: str, status: str) -> None:
        self._db.table("job_steps").upsert(
            {"job_id": job_id, "step_id": step, "status": status}
        ).execute()


