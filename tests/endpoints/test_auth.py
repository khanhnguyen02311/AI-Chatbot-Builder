# pytest can't pass command-line arguments to the test

from fastapi.testclient import TestClient

from backend.main import api_server

client = TestClient(api_server)
client_email = "testclient@email.com"
client_username = "testclient_username"
client_password = "testclient_password"


def test_signup_and_login():
    signup_resp = client.post("/auth/signup", json={"username": client_username, "email": client_email, "password": client_password})
    assert signup_resp.status_code == 200 or signup_resp.content == b"Username or email existed"

    login_resp = client.post("/auth/login", json={"username_or_email": client_username, "password": client_password})
    assert login_resp.status_code == 200
    keys = login_resp.json().keys()
    for key in ["access_token", "refresh_token", "token_type"]:
        assert key in keys


def test_renew_token():
    invalid_resp = client.post("/auth/renew-token", headers={"Authorization": "Bearer invalid_token"})
    assert invalid_resp.status_code == 401 or invalid_resp.content == b"Invalid token"

    login_resp = client.post("/auth/login", json={"username_or_email": client_username, "password": client_password})
    assert login_resp.status_code == 200

    renew_resp = client.post("/auth/renew-token", headers={"Authorization": f"Bearer {login_resp.json()['refresh_token']}"})
    assert renew_resp.status_code == 200
    keys = renew_resp.json().keys()
    for key in ["access_token", "refresh_token", "token_type"]:
        assert key in keys
