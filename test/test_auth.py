import pytest

def test_register_user(client):
    response = client.post(
        "/register",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"

def test_register_existing_user(client):
    # Register first time
    client.post(
        "/register",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    # Register second time
    response = client.post(
        "/register",
        data={"username": "test@example.com", "password": "newpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client):
    # Register user
    client.post(
        "/register",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    # Login
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    # Register user
    client.post(
        "/register",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    # Login with wrong password
    response = client.post(
        "/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"
