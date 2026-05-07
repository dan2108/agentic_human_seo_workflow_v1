def test_reject_gate_requires_comment(client) -> None:
    r = client.post("/gates/nonexistent/reject", json={})
    assert r.status_code in (404, 422)
