def test_create_user(client):
    response = client.post(
        "/users/",
        json = {
            "username" : "testuser",
            "email" : "test@example.com",
            "password" : 'TestPasssword123'
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data

def test_create_duplicate_user(client):
    user = {
        "username" : "duplicateuser",
        "email" : "duplicate@example.com",
        "password" : "TestPassword123"
    }

    first_response = client.post("/users/", json = user)
    assert first_response.status_code == 201

    second_response = client.post("/users/", json = user)
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Username or Email already exists."

def test_get_users(client):
    client.post("/users/", 
                json = {
                    "username" : "listuser",
                    "email" : "list@example.com",
                    "password" : "TestPassword123"
                })

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["username"] == "listuser"

def test_get_users_pagination(client):
    response = client.get("/users/?skip=0&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 1

def test_get_user_by_id(client):
    create_response = client.post("/users/",
                                      json = {
                                          "username" : "getuser",
                                          "email" : "get@example.com",
                                          "password" : "TestPassword123"
                                      })
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "getuser"

def test_get_nonexistent_user(client):
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User Not Found."

def test_update_user(client):
    create_response = client.post("/users/",
                                          json = {
                                              "username" : "getuser",
                                              "email" : "get@example.com",
                                              "password" : "TestPassword123"
                                          })
    user_id = create_response.json()["id"]

    user = {"username" : "updateuser",
            "email" : "updated@example.com"}
    response = client.put(f"/users/{user_id}", json=user)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "updateuser"
    assert data["email"] == "updated@example.com"

def test_delete_user(client):
    create_response = client.post("/users/",
                                          json = {
                                              "username" : "getuser",
                                              "email" : "get@example.com",
                                              "password" : "TestPassword123"
                                          })
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["Message"] == "User data deleted successfully."