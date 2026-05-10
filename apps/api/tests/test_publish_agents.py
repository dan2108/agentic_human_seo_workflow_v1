"""TDD tests for Sprint 4 publish agents + aftercare."""
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock, patch, call

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value.upsert.return_value.execute.return_value = MagicMock()
    db.table.return_value.insert.return_value.execute.return_value = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{'id': 'draft-1', 'job_id': 'job-1', 'body': 'SEO content here.', 'brief_json': {'title': 'SEO Guide', 'target_keyword': 'seo strategy'}, 'outline_json': {}}]
    )
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{'data_json': {'title': 'SEO Guide', 'target_keyword': 'seo strategy'}}]
    )
    return db


class TestCmsAgent:
    @pytest.mark.asyncio
    async def test_run_writes_publish_result_stream(self, mock_db):
        with patch('app.agents.publish.cms_agent.WordPressAdapter') as MockWP:
            mock_wp_inst = AsyncMock()
            mock_wp_inst.publish.return_value = 'https://example.com/seo-guide'
            MockWP.return_value = mock_wp_inst
            from app.agents.publish.cms_agent import CmsAgent
            agent = CmsAgent(mock_db, wp_base_url='https://example.com', wp_app_password='user:pass')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'publish_result'
        assert 'published_url' in upsert_payload['data_json']
        assert result['stream'] == 'publish_result'


class TestLinkingAgent:
    @pytest.mark.asyncio
    async def test_run_writes_linking_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text='{"suggestions": [{"anchor_text": "keyword research", "target_url": "/keyword-research-guide", "context": "...when doing keyword research..."}], "count": 1}')]
        with patch('app.agents.publish.linking_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.publish.linking_agent import LinkingAgent
            agent = LinkingAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'linking'
        assert 'suggestions' in upsert_payload['data_json']
        assert result['stream'] == 'linking'


class TestIndexPingAgent:
    @pytest.mark.asyncio
    async def test_run_writes_index_ping_stream(self, mock_db):
        with patch('httpx.AsyncClient') as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            mock_resp = MagicMock(status_code=200)
            mock_resp.json.return_value = {'urlNotificationMetadata': {'url': 'https://example.com/page', 'latestUpdate': {'type': 'URL_UPDATED'}}}
            ctx.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            from app.agents.publish.index_ping_agent import IndexPingAgent
            agent = IndexPingAgent(mock_db, access_token='fake-token')
            result = await agent.run('job-1', 'https://example.com/page')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'index_ping'
        assert 'status' in upsert_payload['data_json']
        assert result['stream'] == 'index_ping'


class TestDistributionAgent:
    @pytest.mark.asyncio
    async def test_run_writes_distribution_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text='{"linkedin": "Excited to share our new pillar post on SEO strategy!", "twitter": "New guide: seo strategy - everything you need to know. #SEO", "email": "Subject: New Content Published"}')]
        with patch('app.agents.publish.distribution_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.publish.distribution_agent import DistributionAgent
            agent = DistributionAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'distribution'
        assert 'linkedin' in upsert_payload['data_json']
        assert result['stream'] == 'distribution'


class TestSnapshotAgent:
    @pytest.mark.asyncio
    async def test_run_inserts_baseline_snapshot(self, mock_db):
        with patch('httpx.AsyncClient') as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            gsc_resp = MagicMock(status_code=200)
            gsc_resp.json.return_value = {'rows': [{'keys': ['https://example.com'], 'clicks': 10, 'impressions': 200, 'position': 4.5}]}
            dfs_resp = MagicMock(status_code=200)
            dfs_resp.json.return_value = {'tasks': [{'result': [{'items': [{'rank_absolute': 5, 'keyword': 'seo strategy'}]}]}]}
            ctx.post = AsyncMock(side_effect=[gsc_resp, dfs_resp])
            MockClient.return_value = ctx
            from app.agents.aftercare.snapshot_agent import SnapshotAgent
            agent = SnapshotAgent(mock_db, access_token='fake-token', dataforseo_login='u', dataforseo_password='p')
            result = await agent.run('job-1', 'https://example.com')
        mock_db.table.return_value.insert.assert_called_once()
        insert_payload = mock_db.table.return_value.insert.call_args[0][0]
        assert insert_payload['job_id'] == 'job-1'
        assert 'metrics_json' in insert_payload
        assert result.get('stream') == 'snapshot'


class TestAftercareOrchestratorSchedule:
    @pytest.mark.asyncio
    async def test_schedule_enqueues_three_celery_tasks(self):
        with patch('app.orchestrators.aftercare_orchestrator.run_day7_check') as mock_d7, \
             patch('app.orchestrators.aftercare_orchestrator.run_day30_check') as mock_d30, \
             patch('app.orchestrators.aftercare_orchestrator.run_day90_check') as mock_d90:
            from app.orchestrators.aftercare_orchestrator import AftercareOrchestrator
            orch = AftercareOrchestrator()
            await orch.schedule('job-1', '2026-05-08T12:00:00+00:00')
        mock_d7.apply_async.assert_called_once()
        mock_d30.apply_async.assert_called_once()
        mock_d90.apply_async.assert_called_once()
        # Verify eta kwargs present
        d7_kwargs = mock_d7.apply_async.call_args[1]
        assert 'eta' in d7_kwargs
        d30_kwargs = mock_d30.apply_async.call_args[1]
        assert 'eta' in d30_kwargs