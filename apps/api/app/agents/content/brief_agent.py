import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class BriefAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("brief_agent.run", job_id=job_id)

        strategy_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "calendar")
            .execute()
        )
        rows = strategy_row.data or []
        entries = []
        for row in rows:
            entries.extend(row.get("data_json", {}).get("entries", []))

        prompt = (
            "You are an SEO content strategist. Given these content calendar entries, "
            "generate a detailed content brief for the top-priority pillar page. "
            "Return a JSON object with keys: title (string), target_keyword (string), "
            "word_count_target (int), key_sections (array of strings), tone (string).\n\n"
            f"Calendar entries: {json.dumps(entries[:5])}\nSite: {site_url}"
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
            parsed = {"title": "", "target_keyword": "", "word_count_target": 1500,
                      "key_sections": [], "tone": "authoritative"}

        return self._persist(job_id, "brief", parsed)
