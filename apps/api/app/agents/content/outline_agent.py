import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class OutlineAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("outline_agent.run", job_id=job_id)

        brief_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "brief")
            .execute()
        )
        rows = brief_row.data or []
        brief: dict[str, Any] = {}
        if rows:
            brief = rows[0].get("data_json", {})

        prompt = (
            "You are an SEO content strategist. Generate a detailed H2/H3 outline for this content brief. "
            "Return a JSON object with key 'sections', an array of objects each with: "
            "'heading' (H2 string) and 'subheadings' (array of H3 strings).\n\n"
            f"Brief: {json.dumps(brief)}"
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
            parsed = {"sections": []}

        return self._persist(job_id, "outline", parsed)
