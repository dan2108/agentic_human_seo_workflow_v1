import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class CalendarAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("calendar_agent.run", job_id=job_id, site_url=site_url)

        cluster_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "clusters")
            .execute()
        )
        rows = cluster_row.data or []
        clusters: list[dict[str, Any]] = []
        for row in rows:
            clusters.extend(row.get("data_json", {}).get("clusters", []))

        prompt = (
            "Create a 12-week content calendar from these topic clusters. "
            "Return a JSON object with key 'entries', an array of objects each with: "
            "'week' (int 1-12), 'topic' (string), 'keyword' (primary keyword), "
            "'content_type' (one of: pillar, supporting, listicle), 'estimated_traffic' (int).\n\n"
            f"Topic clusters: {json.dumps(clusters)}"
        )

        msg = self._client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = msg.content[0].text
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"entries": []}

        return self._persist(job_id, "calendar", parsed)
