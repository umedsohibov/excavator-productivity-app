from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def make_payload(**overrides):
    payload = {
        "bucket_volume": 1,
        "bucket_fill_factor": 1,
        "cycle_time_seconds": 30,
        "shift_hours": 8,
        "shifts_per_day": 2,
        "working_days_per_year": 330,
        "service_interval_hours": 500,
        "service_duration_hours": 10,
        "emergency_downtime_percent": 5,
        "annual_plan_volume": 500_000,
    }
    payload.update(overrides)
    return payload


def test_index_page_is_available():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_calculate_endpoint_returns_correct_result():
    response = client.post("/calculate", json=make_payload())

    assert response.status_code == 200

    body = response.json()
    assert body["hourly_productivity"] == 120
    assert body["service_count"] == 10
    assert body["plan_is_completed"] is True


def test_calculate_endpoint_rejects_invalid_data():
    response = client.post("/calculate", json=make_payload(bucket_volume=0))

    assert response.status_code == 422


def test_calculate_endpoint_works_without_plan():
    payload = make_payload()
    payload.pop("annual_plan_volume")

    response = client.post("/calculate", json=payload)

    assert response.status_code == 200
    assert response.json()["recommendation"] == "План не задан."
