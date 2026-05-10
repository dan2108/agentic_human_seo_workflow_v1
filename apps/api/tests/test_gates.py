"""Gate route tests — including approve/dispatch wiring."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _mock_db_with_job(site_url: str = "https://example.com") -> MagicMock:
    """Build a mock Supabase client whose jobs.select returns a row with site_url."""
    mock_db = MagicMock()
    # gates.update + job_steps.upsert chain — return self for chaining, .execute returns object with data
    mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[])
    # jobs.select(...).eq(id).limit(1).execute() → row with site_url
    jobs_chain = mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute
    jobs_chain.return_value = MagicMock(data=[{"site_url": site_url}])
    return mock_db


def test_reject_gate_missing_job_id(client):
    """Reject without job_id in path returns 400."""
    mock_db = MagicMock()
    with patch("app.routers.gates.get_supabase", return_value=mock_db):
        r = client.post("/gates/gate1/reject", json={})
    assert r.status_code == 400
    assert "job_id" in r.json()["detail"]


def test_approve_gate_missing_job_id(client):
    """Approve without job_id in path returns 400."""
    mock_db = MagicMock()
    with patch("app.routers.gates.get_supabase", return_value=mock_db):
        r = client.post("/gates/gate1/approve", json={})
    assert r.status_code == 400


def test_approve_gate1_dispatches_research(client):
    """Gate 1 approval must schedule ResearchOrchestrator.dispatch in the background."""
    mock_db = _mock_db_with_job("https://example.com")
    mock_orch = MagicMock()
    mock_orch.return_value.dispatch = AsyncMock()

    with patch("app.routers.gates.get_supabase", return_value=mock_db), \
         patch("app.orchestrators.research_orchestrator.ResearchOrchestrator", mock_orch):
        r = client.post("/gates/gate1:job-abc/approve", json={"comment": "looks good"})

    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "approved"
    assert body["next"] == "research_orchestrator"
    # TestClient runs background tasks before returning — orchestrator should have been called
    mock_orch.return_value.dispatch.assert_awaited_once_with("job-abc", "https://example.com")


def test_approve_gate2_dispatches_content(client):
    """Gate 2 approval schedules ContentOrchestrator."""
    mock_db = _mock_db_with_job("https://example.com")
    mock_orch = MagicMock()
    mock_orch.return_value.dispatch = AsyncMock()

    with patch("app.routers.gates.get_supabase", return_value=mock_db), \
         patch("app.orchestrators.content_orchestrator.ContentOrchestrator", mock_orch):
        r = client.post("/gates/gate2:job-abc/approve", json={"comment": ""})

    assert r.status_code == 200
    assert r.json()["next"] == "content_orchestrator"
    mock_orch.return_value.dispatch.assert_awaited_once_with("job-abc", "https://example.com")


def test_approve_gate3_dispatches_publish(client):
    """Gate 3 approval schedules PublishOrchestrator."""
    mock_db = _mock_db_with_job("https://example.com")
    mock_orch = MagicMock()
    mock_orch.return_value.dispatch = AsyncMock()

    with patch("app.routers.gates.get_supabase", return_value=mock_db), \
         patch("app.orchestrators.publish_orchestrator.PublishOrchestrator", mock_orch):
        r = client.post("/gates/gate3:job-abc/approve", json={"comment": ""})

    assert r.status_code == 200
    assert r.json()["next"] == "publish_orchestrator"
    mock_orch.return_value.dispatch.assert_awaited_once_with("job-abc", "https://example.com")


def test_approve_gate4_schedules_aftercare(client):
    """Gate 4 approval schedules AftercareOrchestrator (Celery enqueue)."""
    mock_db = _mock_db_with_job("https://example.com")
    mock_orch = MagicMock()
    mock_orch.return_value.schedule = AsyncMock()

    with patch("app.routers.gates.get_supabase", return_value=mock_db), \
         patch("app.orchestrators.aftercare_orchestrator.AftercareOrchestrator", mock_orch):
        r = client.post("/gates/gate4:job-abc/approve", json={"comment": ""})

    assert r.status_code == 200
    assert r.json()["next"] == "aftercare_orchestrator"
    mock_orch.return_value.schedule.assert_awaited_once()
    args = mock_orch.return_value.schedule.await_args
    assert args.args[0] == "job-abc"
    # second arg is an ISO timestamp
    assert "T" in args.args[1]


def test_approve_gate1_dispatch_failure_does_not_break_response(client):
    """If the orchestrator import or dispatch raises, gate approval still returns 200."""
    mock_db = _mock_db_with_job("https://example.com")
    mock_orch = MagicMock()
    mock_orch.return_value.dispatch = AsyncMock(side_effect=RuntimeError("boom"))

    with patch("app.routers.gates.get_supabase", return_value=mock_db), \
         patch("app.orchestrators.research_orchestrator.ResearchOrchestrator", mock_orch):
        r = client.post("/gates/gate1:job-abc/approve", json={"comment": ""})

    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_approve_gate1_unknown_job_returns_404(client):
    """If the job doesn't exist, _fetch_site_url raises 404."""
    mock_db = MagicMock()
    mock_db.table.return_value.update.return_value.eq.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    mock_db.table.return_value.upsert.return_value.execute.return_value = MagicMock(data=[])
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])

    with patch("app.routers.gates.get_supabase", return_value=mock_db):
        r = client.post("/gates/gate1:nonexistent/approve", json={"comment": ""})

    assert r.status_code == 404
