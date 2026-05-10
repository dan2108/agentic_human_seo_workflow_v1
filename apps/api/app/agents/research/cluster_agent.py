import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class ClusterAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("cluster_agent.run", job_id=job_id, site_url=site_url)

        intent_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "intent")
            .execute()
        )
        rows = intent_row.data or []
        classifications: list[dict[str, Any]] = []
        for row in rows:
            classifications.extend(row.get("data_json", {}).get("classifications", []))

        prompt = (
            "Group these keyword-intent pairs into topic clusters. "
            "Return a JSON object with key 'clusters', an array of objects each with: "
            "'topic' (string), 'keywords' (array of strings), 'pillar' (bool — true if this is a pillar page topic).\n\n"
            f"Keyword classifications: {json.dumps(classifications)}"
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
            parsed = {"clusters": []}

        return self._persist(job_id, "clusters", parsed)
