from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_user_registration(test_user):
    assert test_user.email.startswith("test_")
    assert test_user.email.endswith("@example.com")


def test_user_login(test_user):
    response = client.post(
        "/api/v1/token",
        json={"email": test_user.email, "password": "password"},
    )
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
