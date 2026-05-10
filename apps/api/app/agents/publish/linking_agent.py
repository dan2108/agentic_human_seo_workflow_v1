import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class LinkingAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("linking_agent.run", job_id=job_id)

        draft_row = (
            self._db.table("content_drafts")
            .select("body")
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        rows = draft_row.data or []
        body = rows[0].get("body", "") if rows else ""

        prompt = (
            "Identify internal linking opportunities in this content. "
            "For each opportunity, provide the anchor text, a suggested target URL path, and the surrounding context. "
            "Return a JSON object with 'suggestions' (array of objects with 'anchor', 'url', 'context') "
            "and 'count' (int).\n\n"
            f"Site: {site_url}\n\nContent:\n{body[:3000]}"
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
            parsed = {"suggestions": [], "count": 0}

        return self._persist(job_id, "linking", parsed)

