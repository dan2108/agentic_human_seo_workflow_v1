"""Publish orchestrator — runs CMS publish + linking + distribution + index ping + baseline snapshot.

Fires when the human approves the content from Gate 3.
Sequences are intentionally serial: snapshot must happen AFTER cms.publish so
the URL exists; index_ping needs the published URL too.
"""
from typing import Any
import structlog

from app.agents.publish.cms_agent import CmsAgent
from app.agents.publish.linking_agent import LinkingAgent
from app.agents.publish.distribution_agent import DistributionAgent
from app.agents.publish.index_ping_agent import IndexPingAgent
from app.agents.aftercare.snapshot_agent import SnapshotAgent

log = structlog.get_logger()


class PublishOrchestrator:
    def __init__(self, db: Any, settings: Any) -> None:
        self._db = db
        self._settings = settings

    def _set_step_status(self, job_id: str, step_id: str, status: str) -> None:
        self._db.table("job_steps").upsert(
            {"job_id": job_id, "step_id": step_id, "status": status}
        ).execute()

    def _fetch_published_url(self, job_id: str) -> str:
        row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "publish_result")
            .execute()
        )
        if not row.data:
            return ""
        return row.data[0].get("data_json", {}).get("published_url", "") or ""

    async def dispatch(self, job_id: str, site_url: str) -> None:
        log.info("publish_orchestrator.dispatch", job_id=job_id)
        s = self._settings

        # 1. CMS publish (must complete first — later steps need published_url)
        try:
            self._set_step_status(job_id, "publish", "running")
            await CmsAgent(self._db, wp_base_url=s.wp_base_url, wp_app_password=s.wp_app_password).run(job_id, site_url)
            self._set_step_status(job_id, "publish", "complete")
        except Exception as exc:
            log.error("cms_agent.failed", job_id=job_id, error=str(exc))
            self._set_step_status(job_id, "publish", "failed")
            return

        published_url = self._fetch_published_url(job_id) or site_url

        # 2-4. Parallel-safe steps (run serially for determinism + simpler error handling)
        for step_id, agent_factory in [
            ("linking", lambda: LinkingAgent(self._db, anthropic_api_key=s.anthropic_api_key)),
            ("distribution", lambda: DistributionAgent(self._db, anthropic_api_key=s.anthropic_api_key)),
            ("index_ping", lambda: IndexPingAgent(self._db, access_token=s.google_access_token)),
            ("snapshot", lambda: SnapshotAgent(
                self._db,
                access_token=s.google_access_token,
                dataforseo_login=s.dataforseo_login,
                dataforseo_password=s.dataforseo_password,
            )),
        ]:
            try:
                self._set_step_status(job_id, step_id, "running")
                # snapshot/index_ping want the published URL; linking/distribution accept either
                target_url = published_url if step_id in {"index_ping", "snapshot"} else site_url
                await agent_factory().run(job_id, target_url)
                self._set_step_status(job_id, step_id, "complete")
            except Exception as exc:
                log.error("publish_step.failed", step_id=step_id, job_id=job_id, error=str(exc))
                self._set_step_status(job_id, step_id, "failed")

        # Gate 4 — human confirms publish; aftercare scheduled on that approval
        self._db.table("gates").upsert(
            {"job_id": job_id, "gate_id": "gate4", "status": "pending"}
        ).execute()
        self._set_step_status(job_id, "gate-4", "awaiting_human")
        log.info("publish_orchestrator.complete", job_id=job_id, url=published_url)
