from app.config import get_settings


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_summary(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert "sensors" in body
    assert body["workforce_filled_percent"] >= 0
    assert body["total_estimated_kw"] > 0


def test_ops_query_requires_api_key(client):
    response = client.post("/api/ops/query", json={"question": "Why is the North gate crowded?"})
    assert response.status_code == 401


def test_ops_query_with_valid_key(client):
    key = get_settings().ops_api_key
    response = client.post(
        "/api/ops/query",
        json={"question": "Why is the North gate crowded?"},
        headers={"X-API-Key": key},
    )
    assert response.status_code == 200
    assert "narrative" in response.json()


def test_transit_route_unknown_city(client):
    response = client.post("/api/transit/route", json={"city": "atlantis", "origin": "downtown"})
    assert response.status_code == 404


def test_transit_route_known_city(client):
    response = client.post("/api/transit/route", json={"city": "miami", "origin": "downtown"})
    assert response.status_code == 200
    assert response.json()["stadium"] == "Hard Rock Stadium"


def test_transit_route_new_city_los_angeles(client):
    response = client.post("/api/transit/route", json={"city": "losangeles", "origin": "downtown"})
    assert response.status_code == 200
    assert response.json()["stadium"] == "SoFi Stadium"


def test_transit_route_new_city_mexico_city(client):
    response = client.post("/api/transit/route", json={"city": "mexico_city", "origin": "centro"})
    assert response.status_code == 200
    assert response.json()["stadium"] == "Estadio Azteca"


def test_accessibility_commentary(client):
    response = client.post(
        "/api/accessibility/commentary",
        json={"event_id": "e4", "language": "English", "verbosity": "brief"},
    )
    assert response.status_code == 200
    assert response.json()["event_id"] == "e4"


def test_workforce_optimize_requires_key(client):
    response = client.post("/api/workforce/optimize")
    assert response.status_code == 401


def test_wayfind_route(client):
    response = client.post("/api/navigation/wayfind", json={"section": "101", "amenity": "restroom"})
    assert response.status_code == 200
    assert response.json()["amenity"] == "restroom"


def test_multilingual_topics_and_faq(client):
    topics = client.get("/api/multilingual/topics")
    assert topics.status_code == 200
    assert len(topics.json()) > 0

    response = client.post("/api/multilingual/faq", json={"topic_id": "gates_open", "language": "English"})
    assert response.status_code == 200
    assert response.json()["topic_id"] == "gates_open"


def test_multilingual_unknown_topic(client):
    response = client.post("/api/multilingual/faq", json={"topic_id": "nonexistent"})
    assert response.status_code == 404


def test_sustainability_report(client):
    response = client.get("/api/sustainability/report")
    assert response.status_code == 200
    body = response.json()
    assert len(body["zones"]) == 5
    assert body["total_estimated_kw"] > 0


def test_multilingual_new_faq_topics(client):
    for topic_id in ("water_policy", "wifi", "prayer_room", "first_aid", "child_policy", "parking"):
        response = client.post("/api/multilingual/faq", json={"topic_id": topic_id, "language": "English"})
        assert response.status_code == 200
        assert response.json()["topic_id"] == topic_id
