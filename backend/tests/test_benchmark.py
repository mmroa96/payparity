import jwt
from fastapi.testclient import TestClient

from app.auth import _SECRET, _ALGORITHM
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_submit_benchmark_happy_path():
    resp = client.post(
        "/api/v1/benchmark",
        json={
            "job_title": "Senior Software Engineer",
            "location": "Seattle, WA",
            "years_experience": 6,
            "current_salary": 145000,
            "department": "Engineering",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["benchmark_id"].startswith("b_")
    assert "predicted_fair_salary" in body
    assert len(body["confidence_interval"]) == 2


def test_submit_benchmark_missing_required_field():
    resp = client.post(
        "/api/v1/benchmark",
        json={"job_title": "Senior Software Engineer", "location": "Seattle, WA"},
    )
    assert resp.status_code == 422


def test_submit_benchmark_negative_experience_rejected():
    resp = client.post(
        "/api/v1/benchmark",
        json={
            "job_title": "Senior Software Engineer",
            "location": "Seattle, WA",
            "years_experience": -1,
            "current_salary": 100000,
        },
    )
    assert resp.status_code == 422


def test_gender_is_not_persisted():
    resp = client.post(
        "/api/v1/benchmark",
        json={
            "job_title": "Senior Software Engineer",
            "location": "Seattle, WA",
            "years_experience": 6,
            "current_salary": 145000,
            "gender": "female",
        },
    )
    assert resp.status_code == 200
    assert "gender" not in resp.json()


def test_get_benchmark_round_trip():
    created = client.post(
        "/api/v1/benchmark",
        json={
            "job_title": "Staff Software Engineer",
            "location": "Remote",
            "years_experience": 10,
            "current_salary": 190000,
        },
    ).json()
    fetched = client.get(f"/api/v1/benchmark/{created['benchmark_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["benchmark_id"] == created["benchmark_id"]


def test_get_benchmark_not_found():
    resp = client.get("/api/v1/benchmark/does-not-exist")
    assert resp.status_code == 404
    assert resp.json()["detail"]["error"] == "not_found"


def test_roles_search():
    resp = client.get("/api/v1/roles", params={"query": "senior"})
    assert resp.status_code == 200
    assert "Senior Software Engineer" in resp.json()["roles"]


def test_bulk_import_requires_auth():
    resp = client.post("/api/v1/salary-data", json={"records": []})
    assert resp.status_code == 401


def test_bulk_import_rejects_non_admin():
    token = jwt.encode({"role": "user"}, _SECRET, algorithm=_ALGORITHM)
    resp = client.post(
        "/api/v1/salary-data",
        json={"records": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_bulk_import_accepts_admin():
    token = jwt.encode({"role": "admin"}, _SECRET, algorithm=_ALGORITHM)
    resp = client.post(
        "/api/v1/salary-data",
        json={
            "records": [
                {"job_title": "Software Engineer II", "location": "Austin, TX", "years_experience": 2, "salary": 95000}
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 202
    assert resp.json()["accepted"] == 1
