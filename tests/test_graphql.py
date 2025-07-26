from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_graphql_endpoint():
    response = client.post("/graphql", json={"query": "{ __schema { types { name } } }"})
    assert response.status_code == 200
    assert "data" in response.json()