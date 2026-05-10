from typing import Any
import structlog

from app.agents.base import BaseAuditAgent
from app.adapters.cms.wordpress import WordPressAdapter

log = structlog.get_logger()


class CmsAgent(BaseAuditAgent):
    def __init__(self, db: Any, wp_base_url: str, wp_app_password: str) -> None:
        super().__init__(db)
        self._wp = WordPressAdapter(base_url=wp_base_url, app_password=wp_app_password)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("cms_agent.run", job_id=job_id)

        draft_row = (
            self._db.table("content_drafts")
            .select("*")
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        rows = draft_row.data or []
        draft = rows[0] if rows else {}

        brief_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "brief")
            .execute()
        )
        brief = brief_row.data[0]["data_json"] if brief_row.data else {}

        content = {
            "title": brief.get("title", ""),
            "content": draft.get("body", ""),
            "status": "publish",
        }
        published_url = await self._wp.publish(content)

        if published_url and brief:
            await self._wp.update_meta(published_url, {
                "title": brief.get("title", ""),
                "description": brief.get("target_keyword", ""),
            })

        data = {"published_url": published_url, "status": "published", "job_id": job_id}
        return self._persist(job_id, "publish_result", data)
