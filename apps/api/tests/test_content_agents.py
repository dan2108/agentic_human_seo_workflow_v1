"""TDD tests for Sprint 3 content + QA agents."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.table.return_value.upsert.return_value.execute.return_value = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(
        data=[{
            'data_json': {
                'entries': [{'week': 1, 'topic': 'SEO Fundamentals', 'keyword': 'seo strategy',
                             'content_type': 'pillar', 'estimated_traffic': 500}],
                'clusters': [{'topic': 'SEO Fundamentals', 'keywords': ['seo strategy'], 'pillar': True}],
                'title': 'The Complete Guide to SEO Strategy',
                'target_keyword': 'seo strategy',
                'word_count_target': 2000,
                'key_sections': ['Introduction', 'Keyword Research'],
                'tone': 'authoritative',
                'sections': [{'heading': 'Introduction', 'subheadings': ['What is SEO?']},
                              {'heading': 'Keyword Research', 'subheadings': ['Finding Keywords']}],
                'body': 'This is a draft about SEO strategy.',
            }
        }]
    )
    return db

BRIEF_JSON = '{"title": "The Complete Guide to SEO Strategy", "target_keyword": "seo strategy", "word_count_target": 2000, "key_sections": ["Introduction", "Keyword Research"], "tone": "authoritative"}'
OUTLINE_JSON = '{"sections": [{"heading": "Introduction", "subheadings": ["What is SEO?"]}, {"heading": "Keyword Research", "subheadings": ["Finding Keywords"]}]}'
EDITOR_JSON = '{"suggestions": [{"type": "tone", "text": "Consider a more direct opening.", "severity": "medium"}], "score": 82}'
FACTCHECK_JSON = '{"claims": [{"claim": "SEO improves traffic", "verified": true, "source": "https://example.com"}], "verified": 1, "issues": 0}'
VOICE_JSON = '{"score": 78, "feedback": "Aligns well with brand voice."}'
PLAGIARISM_RESP = b'<?xml version="1.0"?><response><result count="0"/></response>'


class TestBriefAgent:
    @pytest.mark.asyncio
    async def test_run_writes_brief_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=BRIEF_JSON)]
        with patch('app.agents.content.brief_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.content.brief_agent import BriefAgent
            agent = BriefAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'brief'
        assert 'title' in upsert_payload['data_json']
        assert result['stream'] == 'brief'


class TestOutlineAgent:
    @pytest.mark.asyncio
    async def test_run_writes_outline_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=OUTLINE_JSON)]
        with patch('app.agents.content.outline_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.content.outline_agent import OutlineAgent
            agent = OutlineAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'outline'
        assert 'sections' in upsert_payload['data_json']
        assert result['stream'] == 'outline'


class TestEditorAgent:
    @pytest.mark.asyncio
    async def test_run_writes_editor_review_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=EDITOR_JSON)]
        with patch('app.agents.content.editor_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.content.editor_agent import EditorAgent
            agent = EditorAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'editor_review'
        assert 'suggestions' in upsert_payload['data_json']
        assert result['stream'] == 'editor_review'


class TestFactCheckAgent:
    @pytest.mark.asyncio
    async def test_run_writes_fact_check_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=FACTCHECK_JSON)]
        with patch('app.agents.content.factcheck_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.content.factcheck_agent import FactCheckAgent
            agent = FactCheckAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'fact_check'
        assert 'claims' in upsert_payload['data_json']
        assert result['stream'] == 'fact_check'


class TestVoiceCheckAgent:
    @pytest.mark.asyncio
    async def test_run_writes_voice_check_stream(self, mock_db):
        mock_msg = MagicMock()
        mock_msg.content = [MagicMock(text=VOICE_JSON)]
        with patch('app.agents.qa.voice_check_agent.anthropic.Anthropic') as MockAnthropic:
            mock_inst = MagicMock()
            mock_inst.messages.create.return_value = mock_msg
            MockAnthropic.return_value = mock_inst
            from app.agents.qa.voice_check_agent import VoiceCheckAgent
            agent = VoiceCheckAgent(mock_db, anthropic_api_key='test-key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'voice_check'
        assert 'score' in upsert_payload['data_json']
        assert result['stream'] == 'voice_check'


class TestPlagiarismAgent:
    @pytest.mark.asyncio
    async def test_run_writes_plagiarism_stream(self, mock_db):
        with patch('httpx.AsyncClient') as MockClient:
            ctx = AsyncMock()
            ctx.__aenter__ = AsyncMock(return_value=ctx)
            ctx.__aexit__ = AsyncMock(return_value=None)
            mock_resp = MagicMock(status_code=200)
            mock_resp.content = PLAGIARISM_RESP
            ctx.post = AsyncMock(return_value=mock_resp)
            MockClient.return_value = ctx
            from app.agents.qa.plagiarism_agent import PlagiarismAgent
            agent = PlagiarismAgent(mock_db, copyscape_email='u@u.com', copyscape_apikey='key')
            result = await agent.run('job-1', 'https://example.com')
        upsert_payload = mock_db.table.return_value.upsert.call_args[0][0]
        assert upsert_payload['stream'] == 'plagiarism'
        assert 'duplicate_count' in upsert_payload['data_json']
        assert result['stream'] == 'plagiarism'