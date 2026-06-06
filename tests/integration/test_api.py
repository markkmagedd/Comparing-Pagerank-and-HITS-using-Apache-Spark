from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_pagerank_endpoint_calculation():
    with TestClient(app) as client:
        test_payload = {
            "direction": "buyers",
            "iterations": 1,
            "damping_factor": 0.85,
            "top_n": 5
        }
        response = client.post("/api/pagerank", json=test_payload)
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) <= 5
        if len(data["nodes"]) > 0:
            assert "label" in data["nodes"][0]["data"]
            assert "meta" in data

def test_get_leagues_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/leagues")
        assert response.status_code == 200
        data = response.json()
        assert "leagues" in data
        assert isinstance(data["leagues"], list)
        assert len(data["leagues"]) > 0

def test_pagerank_league_filter_integration():
    with TestClient(app) as client:
        payload = {
            "direction": "buyers",
            "iterations": 1,
            "top_n": 5,
            "league": "Premier League",
            "weight_mode": "fee"
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["league"] == "Premier League"
        assert data["meta"]["empty"] == False

def test_pagerank_weight_mode_integration():
    with TestClient(app) as client:
        payload = {
            "direction": "buyers",
            "iterations": 1,
            "top_n": 5,
            "league": "all",
            "weight_mode": "count"
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["weight_mode"] == "count"
        if len(data["edges"]) > 0:
            assert "deals" in data["edges"][0]["data"]["weight_label"]

def test_pagerank_empty_state_integration():
    with TestClient(app) as client:
        # Using a league name that is unlikely to have intra-league transfers 
        # (e.g. if 'England' was a league but teams were in 'Premier League')
        # In this dataset, most top-level are actual leagues. 
        # Let's try an invalid/fake league to ensure empty state works
        payload = {
            "direction": "buyers",
            "iterations": 1,
            "top_n": 5,
            "league": "NON_EXISTENT_LEAGUE"
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["empty"] == True
        assert len(data["nodes"]) == 0

def test_hits_endpoint():
    with TestClient(app) as client:
        payload = {
            "algorithm": "hits",
            "direction": "buyers",
            "iterations": 1,
            "top_n": 5
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["algorithm"] == "hits"
        assert data["meta"]["score_type"] == "authority"
        assert len(data["nodes"]) > 0
        assert "rank" in data["nodes"][0]["data"]

def test_algorithm_default_backward_compat():
    with TestClient(app) as client:
        # No algorithm field
        payload = {
            "direction": "buyers",
            "top_n": 5
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Should default to pagerank
        assert data["meta"]["algorithm"] == "pagerank"
        assert data["meta"]["score_type"] == "pagerank"

def test_hits_empty_state():
    with TestClient(app) as client:
        payload = {
            "algorithm": "hits",
            "league": "NON_EXISTENT_LEAGUE"
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["empty"] == True
        assert len(data["nodes"]) == 0

def test_hits_with_filters_integration():
    with TestClient(app) as client:
        payload = {
            "algorithm": "hits",
            "league": "Premier League",
            "weight_mode": "count",
            "direction": "sellers",
            "iterations": 2,
            "top_n": 5
        }
        response = client.post("/api/pagerank", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["algorithm"] == "hits"
        assert data["meta"]["score_type"] == "hub"
        assert data["meta"]["league"] == "Premier League"
        assert data["meta"]["weight_mode"] == "count"
        assert len(data["nodes"]) > 0
