import os
import pytest

# SET ENV BEFORE IMPORTING APP
TEST_SECRET = "test_secret_123"
os.environ["API_SECRET_KEY"] = TEST_SECRET

from fastapi.testclient import TestClient
from server.app import app

client = TestClient(app)

def test_tasks_endpoint():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert "tasks" in response.json()

def test_auth_failure():
    # No header
    response = client.post("/baseline")
    assert response.status_code == 422 # missing required header Field
    
    # Wrong header
    response = client.post("/baseline", headers={"X-API-Key": "wrong-secret"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API Key"

def test_grader_validation():
    # Valid payload
    valid_payload = {"episode_id": "ep123", "total_reward": 2.5}
    response = client.post("/grader", json=valid_payload, headers={"X-API-Key": TEST_SECRET})
    assert response.status_code == 200
    assert response.json()["score"] == 2.5
    
    # Missing episode_id
    invalid_payload = {"total_reward": 2.5}
    response = client.post("/grader", json=invalid_payload, headers={"X-API-Key": TEST_SECRET})
    assert response.status_code == 400
    
    # Invalid reward bounds
    out_of_bounds = {"episode_id": "ep123", "total_reward": 5.0}
    response = client.post("/grader", json=out_of_bounds, headers={"X-API-Key": TEST_SECRET})
    assert response.status_code == 400
