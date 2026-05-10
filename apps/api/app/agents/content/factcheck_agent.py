import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class FactCheckAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("factcheck_agent.run", job_id=job_id)

        draft_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "draft")
            .execute()
        )
        rows = draft_row.data or []
        body = rows[0].get("data_json", {}).get("body", "") if rows else ""

        prompt = (
            "Identify factual claims in this content draft and assess their verifiability. "
            "Return a JSON object with: 'claims' (array of objects with 'claim' string, 'verified' bool, 'source' string), "
            "'verified' (int count of verified claims), 'issues' (int count of unverified/disputed claims).\n\n"
            f"Content:\n{body[:3000]}\nSite URL: {site_url}"
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
            parsed = {"claims": [], "verified": 0, "issues": 0}

        return self._persist(job_id, "fact_check", parsed)
