"""TDD tests for Sprint 1 audit agents."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value.upsert.return_value.execute.return_value = MagicMock()
    return db


@pytest.fixture
def html_fixture():
    return (
        "<html><head>"
        "<title>Test Page Title</title>"
        "<meta name='description' content='A test description'>"
        "<link rel='canonical' href='https://example.com/'>"
        "</head><body>"
        "<h1>Main Heading</h1>"
        "<h2>Sub Heading</h2>"
        "<p>This is some content with enough words to not be thin content.</p>"
        "<script async src='https://www.googletagmanager.com/gtag/js?id=G-ABC123'></script>"
        "</body></html>"
    )


class TestCrawlAgent:
    @pytest.mark.asyncio
    async def test_run_writes_crawl_stream(self, mock_db, html_fixture):
        from app.agents.audit.crawl_agent import CrawlAgent
        agent = CrawlAgent(mock_db)
        mock_resp = MagicMock(status_code=200, text=html_fixture, url="https://example.com/")
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            ctx.get = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["job_id"] == "job-1"
        assert upsert_payload["stream"] == "crawl"
        assert "pages" in upsert_payload["data_json"]
        assert result["stream"] == "crawl"


class TestTechnicalAgent:
    @pytest.mark.asyncio
    async def test_run_writes_technical_stream(self, mock_db, html_fixture):
        from app.agents.audit.technical_agent import TechnicalAgent
        agent = TechnicalAgent(mock_db)
        mock_resp = MagicMock(status_code=200, text=html_fixture, elapsed=MagicMock(total_seconds=MagicMock(return_value=0.25)))
        mock_robots = MagicMock(status_code=200)
        mock_sitemap = MagicMock(status_code=200)
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            ctx.get = AsyncMock(side_effect=[mock_resp, mock_robots, mock_sitemap])
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "technical"
        assert "ttfb_ms" in upsert_payload["data_json"]
        assert result["stream"] == "technical"


class TestOnPageAgent:
    @pytest.mark.asyncio
    async def test_run_writes_onpage_stream(self, mock_db, html_fixture):
        from app.agents.audit.onpage_agent import OnPageAgent
        agent = OnPageAgent(mock_db)
        mock_resp = MagicMock(status_code=200, text=html_fixture)
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            ctx.get = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "onpage"
        d = upsert_payload["data_json"]
        assert "title" in d
        assert "meta_description" in d
        assert "h1" in d
        assert result["stream"] == "onpage"


class TestContentAuditAgent:
    @pytest.mark.asyncio
    async def test_run_writes_content_stream(self, mock_db, html_fixture):
        mock_resp = MagicMock(status_code=200, text=html_fixture)
        mock_claude_msg = MagicMock()
        mock_claude_msg.content = [MagicMock(text='{"thin_content": false, "word_count": 45, "topics": ["test"]}')]
        with patch("httpx.AsyncClient") as MockClient, \
             patch("app.agents.audit.content_audit_agent.anthropic.Anthropic") as MockAnthropic:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            ctx.get = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            mock_anthropic_inst = MagicMock()
            mock_anthropic_inst.messages.create.return_value = mock_claude_msg
            MockAnthropic.return_value = mock_anthropic_inst
            from app.agents.audit.content_audit_agent import ContentAuditAgent
            agent = ContentAuditAgent(mock_db, anthropic_api_key="test-key")
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "content"
        assert "word_count" in upsert_payload["data_json"]
        assert result["stream"] == "content"


class TestAuthorityAgent:
    @pytest.mark.asyncio
    async def test_run_writes_authority_stream(self, mock_db):
        from app.agents.audit.authority_agent import AuthorityAgent
        agent = AuthorityAgent(mock_db, ahrefs_api_key="test-key")
        mock_ahrefs_data = {"domain_rating": 45, "organic_traffic": 1200, "referring_domains": 320}
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            mock_resp = MagicMock(status_code=200)
            mock_resp.json.return_value = mock_ahrefs_data
            ctx.get = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "authority"
        assert "domain_rating" in upsert_payload["data_json"]
        assert result["stream"] == "authority"


class TestCompetitiveAgent:
    @pytest.mark.asyncio
    async def test_run_writes_competitive_stream(self, mock_db):
        from app.agents.audit.competitive_agent import CompetitiveAgent
        agent = CompetitiveAgent(mock_db, dataforseo_login="u", dataforseo_password="p")
        mock_resp_data = {"tasks": [{"result": [{"items": [{"keyword": "seo tool", "rank_absolute": 12}]}]}]}
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            mock_resp = MagicMock(status_code=200)
            mock_resp.json.return_value = mock_resp_data
            ctx.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "competitive"
        assert "ranked_keywords" in upsert_payload["data_json"]
        assert result["stream"] == "competitive"


class TestAnalyticsAgent:
    @pytest.mark.asyncio
    async def test_run_detects_ga4_tag(self, mock_db, html_fixture):
        from app.agents.audit.analytics_agent import AnalyticsAgent
        agent = AnalyticsAgent(mock_db)
        mock_resp = MagicMock(status_code=200, text=html_fixture)
        with patch("httpx.AsyncClient") as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            ctx.get = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            result = await agent.run("job-1", "https://example.com")
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload["stream"] == "analytics"
        d = upsert_payload["data_json"]
        assert "has_ga4" in d
        assert d["has_ga4"] is True
        assert d["measurement_id"] == "G-ABC123"
        assert result["stream"] == "analytics"
