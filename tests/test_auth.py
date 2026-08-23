def test_login(client, test_user):
    user = {"username" : test_user["username"],
            "password" : "TestPassword123"}
    response = client.post("/auth/login", data = user)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    user = {"username" : test_user["username"],
            "password" : "WrongPassword"}
    response = client.post("/auth/login", data = user)
    assert response.status_code == 401

def test_login_wrong_username(client):
    user = {
        "username" : "doesnotexist",
        "password" : "TestPassword123"
    }
    response = client.post("/auth/login", data = user)
    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    response = client.get("auth/me")
    assert response.status_code == 401

def test_get_current_user(client, test_user, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user["id"]
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]