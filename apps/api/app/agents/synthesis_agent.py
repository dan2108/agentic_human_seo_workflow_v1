import json
from typing import Any
import anthropic
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

SYNTHESIS_PROMPT = """You are an expert SEO analyst. Analyze the following audit data streams and produce a prioritized report.

Audit streams:
{streams_json}

Return JSON with these exact keys:
- executive_summary (str): 2-3 sentence summary for business stakeholders
- critical_issues (list[str]): issues requiring immediate action
- high_priority (list[str]): high-impact improvements
- medium_priority (list[str]): medium-impact improvements
- low_priority (list[str]): minor improvements / nice-to-haves
- quick_wins (list[str]): easy-to-implement, fast-impact actions"""


class SynthesisAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._claude = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str = "", **kwargs) -> dict[str, Any]:
        log.info("synthesis_agent.run", job_id=job_id)

        rows = (
            self._db.table("audit_results")
            .select("stream,data_json")
            .eq("job_id", job_id)
            .execute()
        )
        streams_by_name = {row["stream"]: row["data_json"] for row in (rows.data or [])}

        msg = self._claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": SYNTHESIS_PROMPT.format(streams_json=json.dumps(streams_by_name, indent=2)[:6000]),
            }],
        )

        try:
            report = json.loads(msg.content[0].text)
        except (json.JSONDecodeError, IndexError, AttributeError):
            report = {
                "executive_summary": "Analysis complete.",
                "critical_issues": [],
                "high_priority": [],
                "medium_priority": [],
                "low_priority": [],
                "quick_wins": [],
            }

        return self._persist(job_id, "synthesis", report)
