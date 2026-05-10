import re
from typing import Any
import httpx
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

COPYSCAPE_URL = "https://www.copyscape.com/api/"


class PlagiarismAgent(BaseAuditAgent):
    def __init__(self, db: Any, copyscape_email: str, copyscape_apikey: str) -> None:
        super().__init__(db)
        self._email = copyscape_email
        self._apikey = copyscape_apikey

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("plagiarism_agent.run", job_id=job_id)

        draft_row = (
            self._db.table("audit_results")
            .select("data_json")
            .eq("job_id", job_id)
            .eq("stream", "draft")
            .execute()
        )
        rows = draft_row.data or []
        body = rows[0].get("data_json", {}).get("body", "") if rows else ""

        payload = {
            "u": self._email,
            "k": self._apikey,
            "o": "csearch",
            "f": "n",
            "e": "UTF-8",
            "c": "10",
            "t": body[:10000],
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(COPYSCAPE_URL, data=payload)

        duplicate_count = 0
        sources: list[dict[str, Any]] = []
        if resp.status_code == 200:
            xml = resp.content.decode("utf-8", errors="replace")
            counts = re.findall(r'count="(\d+)"', xml)
            if counts:
                duplicate_count = int(counts[0])

        data = {"duplicate_count": duplicate_count, "sources": sources, "checked_chars": len(body)}
        return self._persist(job_id, "plagiarism", data)
