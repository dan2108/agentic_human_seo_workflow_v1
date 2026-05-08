"""Gate route tests."""
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_reject_gate_missing_job_id(client):
    """Gate reject without job_id in the path should return 400."""
    mock_db = MagicMock()
    with patch("app.routers.gates.get_supabase", return_value=mock_db):
        r = client.post("/gates/gate1/reject", json={})
    assert r.status_code == 400
    assert "job_id" in r.json()["detail"]
