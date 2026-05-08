"""Tests for SynthesisAgent and SEOOrchestrator."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value.upsert.return_value.execute.return_value = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[
            {"stream": "crawl", "data_json": {"pages": [{"url": "https://example.com", "status_code": 200}]}},
            {"stream": "technical", "data_json": {"ttfb_ms": 250}},
            {"stream": "onpage", "data_json": {"title": "Test", "h1": "Heading", "word_count": 450}},
            {"stream": "content", "data_json": {"thin_content": False, "word_count": 450}},
            {"stream": "authority", "data_json": {"domain_rating": 45}},
            {"stream": "competitive", "data_json": {"ranked_keywords_count": 5}},
            {"stream": "analytics", "data_json": {"has_ga4": True}},
        ]
    )
    db.table.return_value.insert.return_value.execute.return_value = MagicMock()
    db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
    return db


class TestSynthesisAgent:
    @pytest.mark.asyncio
    async def test_run_writes_synthesis_stream(self, mock_db):
        mock_claude_msg = MagicMock()
        RESP = '{"executive_summary": "Good site", "critical_issues": [], "high_priority": ["Speed"], "medium_priority": [], "low_priority": []}'
        mock_claude_msg.content = [MagicMock(text=RESP)]

        with patch("app.agents.synthesis_agent.anthropic.Anthropic") as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_claude_msg
            MockAnthropic.return_value = mock_inst

            from app.agents.synthesis_agent import SynthesisAgent
            agent = SynthesisAgent(mock_db, anthropic_api_key="test-key")
            result = await agent.run("job-1", site_url="https://example.com")

        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "synthesis"
        assert "executive_summary" in upsert_payload["data_json"]
        assert result["stream"] == "synthesis"


class TestSEOOrchestrator:
    @pytest.mark.asyncio
    async def test_dispatch_creates_job_steps(self, mock_db):
        with patch("app.orchestrators.seo_orchestrator.CrawlAgent"), \
             patch("app.orchestrators.seo_orchestrator.TechnicalAgent"), \
             patch("app.orchestrators.seo_orchestrator.OnPageAgent"), \
             patch("app.orchestrators.seo_orchestrator.ContentAuditAgent"), \
             patch("app.orchestrators.seo_orchestrator.AuthorityAgent"), \
             patch("app.orchestrators.seo_orchestrator.CompetitiveAgent"), \
             patch("app.orchestrators.seo_orchestrator.AnalyticsAgent"), \
             patch("app.orchestrators.seo_orchestrator.SynthesisAgent"):
            from app.orchestrators.seo_orchestrator import SEOOrchestrator
            orch = SEOOrchestrator(mock_db, settings=MagicMock())
            await orch.dispatch("job-1", "https://example.com")

        assert mock_db.table.call_count >= 1
