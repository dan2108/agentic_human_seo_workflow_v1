def test_health(client) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_job_rejects_invalid_url(client) -> None:
    r = client.post("/jobs/", json={"site_url": "not-a-url", "business_goal": "x", "icp": "x", "brand_voice": "x"})
    assert r.status_code == 422
