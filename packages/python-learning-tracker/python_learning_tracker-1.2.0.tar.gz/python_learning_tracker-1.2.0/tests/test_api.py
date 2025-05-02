import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from python_learning_tracker.api import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_status_code(client):
    response = client.get("/")
    assert response.status_code == 200


def test_home_contains_available_endpoints(client):
    response = client.get("/")
    data = response.get_json()
    assert "available_endpoints" in data
    assert "/api/v1/reports" in data["available_endpoints"]
    assert "/apidocs" in data["available_endpoints"]


def test_reports_status_code_200(client):
    response = client.get("/api/v1/reports")
    assert response.status_code == 200


def test_reports_has_expected_fields(client):
    response = client.get("/api/v1/reports")
    data = response.get_json()
    assert isinstance(data, list)
    if data:  # Якщо список не порожній — перевіряємо ключі
        item = data[0]
        assert all(key in item for key in ["theme", "planned", "actual", "score", "recommendation"])


def test_reports_format_xml(client):
    response = client.get("/api/v1/reports?format=xml")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/xml")
    assert b"<report>" in response.data


def test_reports_filter_by_topic(client):
    response = client.get("/api/v1/reports?topic=OOP")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for item in data:
        assert "OOP" in item["theme"].upper() or "OOP" in item["abbr"].upper()


def test_reports_filter_by_date_range(client):
    response = client.get("/api/v1/reports?start_date=2024-01-01&end_date=2024-12-31")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_reports_topic_not_found(client):
    response = client.get("/api/v1/reports?topic=NONEXISTENT")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data == []


def test_reports_invalid_format_param(client):
    response = client.get("/api/v1/reports?format=yaml")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")


def test_reports_invalid_date_format(client):
    response = client.get("/api/v1/reports?start_date=абракадабра")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid date format" in data.get("details", "")


def test_topics_status_code_200(client):
    response = client.get("/api/v1/topics")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    if data:
        assert "abbr" in data[0]
        assert "theme" in data[0]


def test_topics_sorted_desc(client):
    response = client.get("/api/v1/topics?order=desc")
    assert response.status_code == 200
    data = response.get_json()
    themes = [t["theme"] for t in data]
    assert themes == sorted(themes, reverse=True)


def test_topics_format_xml(client):
    response = client.get("/api/v1/topics?format=xml")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/xml")
    assert b"<report>" in response.data


def test_search_returns_results(client):
    response = client.get("/api/v1/search?q=oop")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    for item in data:
        assert "abbr" in item
        assert "theme" in item


def test_search_missing_query_param(client):
    response = client.get("/api/v1/search")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data or "message" in data
