import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class DistributionAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("distribution_agent.run", job_id=job_id)

        draft_row = (
            self._db.table("content_drafts")
            .select("body,brief_json")
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        rows = draft_row.data or []
        draft = rows[0] if rows else {}
        body = draft.get("body", "")
        brief = draft.get("brief_json") or {}

        title = brief.get("title", "")
        keyword = brief.get("target_keyword", "")

        prompt = (
            "Draft distribution copy for this published content. "
            "Return a JSON object with: 'linkedin' (professional post, 150-200 words), "
            "'twitter' (280 chars max, include hashtags), 'email' (subject + 3-paragraph body).\n\n"
            f"Title: {title}\nTarget keyword: {keyword}\nContent excerpt: {body[:500]}\nURL: {site_url}"
        )

        msg = self._client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = msg.content[0].text
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"linkedin": "", "twitter": "", "email": ""}

        return self._persist(job_id, "distribution", parsed)
