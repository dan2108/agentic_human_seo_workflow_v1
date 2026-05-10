"""Tests for aftercare agents (Day 7 / 30 / 90 + Monitor)."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.agents.aftercare.day7_agent import Day7Agent
from app.agents.aftercare.day30_agent import Day30Agent
from app.agents.aftercare.day90_agent import Day90Agent, _classify_outcome
from app.agents.aftercare.monitor_agent import MonitorAgent


def _baseline_row(url="https://example.com/post", metrics=None):
    return MagicMock(data=[{
        "url": url,
        "metrics_json": metrics or {"impressions": 100, "clicks": 5, "position": 12.0, "rank": 12},
    }])


def test_classify_winner():
    outcome, ambiguous = _classify_outcome({"rank": -6}, {"clicks": 20}, {"clicks": 5})
    assert outcome == "winner"
    assert ambiguous is False


def test_classify_loser_by_rank_drop():
    outcome, _ = _classify_outcome({"rank": 16}, {"clicks": 5}, {"clicks": 5})
    assert outcome == "loser"


def test_classify_loser_by_clicks_collapse():
    outcome, _ = _classify_outcome({"rank": 2}, {"clicks": 0}, {"clicks": 100})
    assert outcome == "loser"


def test_classify_underperformer():
    outcome, _ = _classify_outcome({"rank": 6}, {"clicks": 4}, {"clicks": 5})
    assert outcome == "underperformer"


def test_classify_steady():
    outcome, ambiguous = _classify_outcome({"rank": 1}, {"clicks": 5}, {"clicks": 5})
    assert outcome == "steady"
    assert ambiguous is False


def test_classify_ambiguous_falls_through():
    outcome, ambiguous = _classify_outcome({"rank": -10}, {"clicks": 4}, {"clicks": 5})
    assert ambiguous is True


@pytest.mark.asyncio
async def test_day7_no_baseline_returns_empty():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    agent = Day7Agent(mock_db, "tok", "u", "p")
    result = await agent.run("job-1")
    assert result == {}


@pytest.mark.asyncio
async def test_day7_persists_to_aftercare_reports():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = _baseline_row()

    agent = Day7Agent(mock_db, "tok", "u", "p")

    with patch.object(agent, "_fetch_gsc", new=AsyncMock(return_value={"impressions": 250, "clicks": 12, "position": 9.0, "indexed": True})), \
         patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=8)):
        report = await agent.run("job-1")

    assert report["indexed"] is True
    assert report["delta"]["rank"] == 8 - 12
    upsert_calls = mock_db.table.return_value.upsert.call_args_list
    assert any(c.args[0].get("checkpoint") == "day7" for c in upsert_calls)


@pytest.mark.asyncio
async def test_day30_persists_with_backlinks():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = _baseline_row()

    agent = Day30Agent(mock_db, "tok", "u", "p", "ahrefs")

    with patch.object(agent, "_fetch_gsc", new=AsyncMock(return_value={"impressions": 500, "clicks": 25, "position": 7.0})), \
         patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=6)), \
         patch.object(agent, "_fetch_backlinks", new=AsyncMock(return_value={"count": 3, "referring_domains": 2})):
        report = await agent.run("job-1")

    assert report["current"]["backlinks"]["count"] == 3
    upsert_calls = mock_db.table.return_value.upsert.call_args_list
    assert any(c.args[0].get("checkpoint") == "day30" for c in upsert_calls)


@pytest.mark.asyncio
async def test_day90_writes_both_report_and_outcome():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = _baseline_row()

    agent = Day90Agent(mock_db, "tok", "u", "p", "ahrefs", "anthropic")

    with patch.object(agent, "_fetch_gsc", new=AsyncMock(return_value={"impressions": 800, "clicks": 12, "position": 5.0})), \
         patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=6)), \
         patch.object(agent, "_fetch_backlinks", new=AsyncMock(return_value={"count": 5, "referring_domains": 4})), \
         patch.object(agent, "_generate_narrative", return_value="Great quarter for this asset."):
        report = await agent.run("job-1")

    assert report["outcome"] == "winner"
    assert report["narrative"] == "Great quarter for this asset."

    upserts = mock_db.table.return_value.upsert.call_args_list
    assert any(c.args[0].get("checkpoint") == "day90" for c in upserts)
    assert any(c.args[0].get("outcome") == "winner" for c in upserts)


@pytest.mark.asyncio
async def test_day90_ambiguous_calls_llm_classifier():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value = _baseline_row()

    agent = Day90Agent(mock_db, "tok", "u", "p", "ahrefs", "anthropic")

    with patch.object(agent, "_fetch_gsc", new=AsyncMock(return_value={"impressions": 200, "clicks": 4, "position": 4.0})), \
         patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=2)), \
         patch.object(agent, "_fetch_backlinks", new=AsyncMock(return_value={"count": 0, "referring_domains": 0})), \
         patch.object(agent, "_llm_classify", return_value="underperformer") as mock_llm, \
         patch.object(agent, "_generate_narrative", return_value=""):
        report = await agent.run("job-1")

    mock_llm.assert_called_once()
    assert report["outcome"] == "underperformer"


@pytest.mark.asyncio
async def test_monitor_emits_warning_on_10_position_drop():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"job_id": "j1", "url": "https://example.com", "metrics_json": {"rank": 5}}]
    )

    agent = MonitorAgent(mock_db, "u", "p")
    with patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=15)):
        result = await agent.run()

    assert result["alerts"] == 1
    insert_calls = mock_db.table.return_value.insert.call_args_list
    assert any(c.args[0].get("severity") == "warning" for c in insert_calls)


@pytest.mark.asyncio
async def test_monitor_emits_critical_on_20_position_drop():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"job_id": "j1", "url": "https://example.com", "metrics_json": {"rank": 5}}]
    )

    agent = MonitorAgent(mock_db, "u", "p")
    with patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=30)):
        result = await agent.run()

    assert result["alerts"] == 1
    insert_calls = mock_db.table.return_value.insert.call_args_list
    assert any(c.args[0].get("severity") == "critical" for c in insert_calls)


@pytest.mark.asyncio
async def test_monitor_silent_on_stable_rank():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock(
        data=[{"job_id": "j1", "url": "https://example.com", "metrics_json": {"rank": 5}}]
    )

    agent = MonitorAgent(mock_db, "u", "p")
    with patch.object(agent, "_fetch_rank", new=AsyncMock(return_value=6)):
        result = await agent.run()

    assert result["alerts"] == 0
    assert len(mock_db.table.return_value.insert.call_args_list) == 0
