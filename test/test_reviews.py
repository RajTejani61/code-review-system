import pytest
import io

def get_auth_header(client, email="test@example.com", password="testpassword"):
    client.post("/register", data={"username": email, "password": password})
    response = client.post("/login", data={"username": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_request_review(client):
    headers = get_auth_header(client)
    
    # Create a dummy file
    file_content = b"def hello():\n    print('world')"
    file = io.BytesIO(file_content)
    
    response = client.post(
        "/review/",
        headers=headers,
        files={"file": ("test.py", file, "text/x-python")},
        data={"language": "python"}
    )
    
    assert response.status_code == 201
    assert "review_id" in response.json()
    assert response.json()["status"] == "pending"

def test_get_review_status(client):
    headers = get_auth_header(client)
    
    # Submit review
    file_content = b"def hello():\n    print('world')"
    file = io.BytesIO(file_content)
    submit_res = client.post(
        "/review/",
        headers=headers,
        files={"file": ("test.py", file, "text/x-python")},
        data={"language": "python"}
    )
    review_id = submit_res.json()["review_id"]
    
    # Get status
    response = client.get(f"/review/{review_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == review_id
    assert response.json()["status"] in ["pending", "processing", "completed", "failed"]

def test_get_all_user_reviews(client):
    headers = get_auth_header(client)
    
    # Submit a review
    file_content = b"def hello():\n    print('world')"
    file = io.BytesIO(file_content)
    client.post(
        "/review/",
        headers=headers,
        files={"file": ("test.py", file, "text/x-python")},
        data={"language": "python"}
    )
    
    # Get all reviews
    response = client.get("/review/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1

def test_unauthorized_review_access(client):
    headers_user1 = get_auth_header(client, "user1@example.com")
    headers_user2 = get_auth_header(client, "user2@example.com")
    
    # User 1 submits a review
    file_content = b"def hello():\n    print('world')"
    file = io.BytesIO(file_content)
    submit_res = client.post(
        "/review/",
        headers=headers_user1,
        files={"file": ("test.py", file, "text/x-python")},
        data={"language": "python"}
    )
    review_id = submit_res.json()["review_id"]
    
    # User 2 tries to access User 1's review
    response = client.get(f"/review/{review_id}", headers=headers_user2)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorised to view this review"
