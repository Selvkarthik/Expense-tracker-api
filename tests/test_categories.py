def test_create_category(client):
    data = {"name" : "Food"}
    response = client.post("/categories/", json=data)
    assert response.status_code == 201
    cat_data = response.json()
    assert cat_data["name"] == "Food"
    assert "id" in cat_data

def test_duplicate_categories(client):
    data = {"name" : "Food"}
    response = client.post("/categories/", json=data)
    assert response.status_code == 201

    second_response = client.post("/categories", json=data)
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Category already exists."

def test_get_categories(client, test_category):
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert isinstance(data, list)
    assert data[0]["name"] == test_category["name"]

def test_get_categories_by_id(client, test_category):
    cat_id = test_category["id"]

    response = client.get(f"/categories/{cat_id}")
    assert response.status_code == 200
    assert response.json()["id"] == cat_id

def test_get_nonexistent_category(client):
    response = client.get("/categories/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category Not Found."

def test_update_category(client, test_category):
    cat_id = test_category["id"]

    response = client.put(f"/categories/{cat_id}",
                          json={
                              "name" : "Groceries"
                          })
    assert response.status_code == 200
    assert response.json()["id"] == cat_id
    assert response.json()["name"] == "Groceries"

    response1 = client.put('/categories/123', json={"name" : "Travel"})
    assert response1.status_code == 404
    assert response1.json()['detail'] == 'Category does not Exist.'

def test_duplicate_update_category(client, test_category):
    create2 = client.post("/categories/", json = {"name" : "Travel"})
    cat_id = create2.json()["id"]

    response = client.put(f"/categories/{cat_id}", json = {"name" : "Food"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Category already exists."

def test_delete_category(client, test_category):
    cat_id = test_category["id"]

    response = client.delete(f"/categories/{cat_id}")
    assert response.status_code == 200

    resp1 = client.get(f"/categories/{cat_id}")
    assert resp1.status_code == 404
    assert resp1.json()['detail'] == "Category Not Found."

    resp2 = client.delete('/categories/23')
    assert resp2.status_code == 404
    assert resp2.json()['detail'] == "Category Not Found."

def test_delete_category_used_by_expense(client, auth_headers, test_category):
    cat_id = test_category["id"]

    exp_create = client.post("/expenses/", headers = auth_headers,
                             json = {
                                 "title" : "Food",
                                 "amount" : 1000,
                                 "description" : "Dinner",
                                 "expense_date" : "2026-05-11",
                                 "category_id" : cat_id
                             })
    assert exp_create.status_code == 201
    
    del_cat = client.delete(f"/categories/{cat_id}")
    assert del_cat.status_code == 409
    assert del_cat.json()["detail"] == "Category cannot be deleted because it is being used by an expense."