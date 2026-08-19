def test_login(client):
    data = {"username" : "loginuser",
            "email" : "login@example.com",
            "password" : "TestPassword123"}
    create_response = client.post("/users/", json = data)
    assert create_response.status_code == 201

    user = {"username" : "loginuser",
            "password" : "TestPassword123"}
    response = client.post("/auth/login", data = user)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    user = {"username" : "updateuser",
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