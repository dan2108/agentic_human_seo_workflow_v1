import json
import re
from typing import Any
import httpx
import anthropic
from bs4 import BeautifulSoup
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

CONTENT_ANALYSIS_PROMPT = """Analyze the following page content for SEO quality.
Return JSON with these exact keys:
- thin_content (bool): true if word count < 300
- word_count (int): total words
- topics (list[str]): main topics identified (max 5)
- content_quality_score (int): 1-10 scale
- issues (list[str]): any content quality issues

Page text:
{text}"""


class ContentAuditAgent(BaseAuditAgent):
    def __init__(self, db: Any, anthropic_api_key: str) -> None:
        super().__init__(db)
        self._claude = anthropic.Anthropic(api_key=anthropic_api_key)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("content_audit_agent.run", job_id=job_id)

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(site_url)

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(re.findall(r"\w+", text))

        msg = self._claude.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": CONTENT_ANALYSIS_PROMPT.format(text=text[:3000])}],
        )
        try:
            analysis = json.loads(msg.content[0].text)
        except (json.JSONDecodeError, IndexError, AttributeError):
            analysis = {"thin_content": word_count < 300, "word_count": word_count, "topics": [], "content_quality_score": 5, "issues": []}

        data = {"word_count": word_count, **analysis}
        return self._persist(job_id, "content", data)
