import json
from typing import Any
import anthropic
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class VoiceCheckAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._client = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("voice_check_agent.run", job_id=job_id)

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
            "Evaluate this content draft for brand voice alignment. "
            "Brand voice: professional, authoritative, clear, and helpful. "
            "Return a JSON object with: 'score' (int 0-100, where 100 = perfect alignment) "
            "and 'feedback' (string with actionable suggestions).\n\n"
            f"Content:\n{body[:3000]}"
        )

        msg = self._client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = msg.content[0].text
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"score": 0, "feedback": "Unable to parse response."}

        return self._persist(job_id, "voice_check", parsed)
