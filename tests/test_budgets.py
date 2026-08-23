def test_create_budget(client, auth_headers):
    response = client.post('/budgets/', headers=auth_headers,
                           json={
                               "month" : 8,
                               "year" : 2026,
                               "limit_amount" : "25000"
                           })
    assert response.status_code == 201
    data = response.json()
    assert data["month"] == 8
    assert data["year"] == 2026
    assert data["limit_amount"] == "25000.00"

    response1 = client.post('/budgets/', headers=auth_headers,
                               json={
                                   "month" : 8,
                                   "year" : 2026,
                                   "limit_amount" : "25000"
                               })
    assert response1.status_code == 409

def test_get_budgets(client, auth_headers, test_budgets):
    client.post('/budgets/', headers=auth_headers,
                json={
                    "month" : 9,
                    "year" : 2026,
                    "limit_amount" : 30000
                })
    response = client.get('/budgets/', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]['month'] == 8
    assert data[1]['month'] == 9
    assert data[0]['limit_amount'] == "25000.00"
    assert data[1]['limit_amount'] == "30000.00"

def test_get_budget_by_id(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    response = client.get(f'/budgets/{budget_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['month'] == 8
    assert data['year'] == 2026
    assert data['limit_amount'] == '25000.00'

    response1 = client.get(f'/budgets/123', headers=auth_headers)
    assert response1.status_code == 404
    assert response1.json()['detail'] == 'Budget data not Found.'

def test_update_budget(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    response = client.put(f'/budgets/{budget_id}', headers=auth_headers,
                          json = {
                              'month' : 9,
                              'year' : 2026,
                              'limit_amount' : "30000.00"
                          })
    assert response.status_code == 200
    data = response.json()
    assert data['month'] == 9
    assert data['year'] == 2026
    assert data['limit_amount'] == '30000.00'

def test_update_duplicate_budget(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    response = client.post('/budgets/', headers=auth_headers,
                          json = {
                              'month' : 9,
                              'year' : 2026,
                              'limit_amount' : "30000.00"
                          })
    assert response.status_code == 201
    data = response.json()
    budget_id = data['id']

    response1 = client.put(f'/budgets/{budget_id}', headers=auth_headers,
                              json = {
                                  'month' : 8,
                                  'year' : 2026,
                                  'limit_amount' : "30000.00"
                              })
    assert response1.status_code == 409
    assert response1.json()['detail'] == 'Cannot update Budget already exists.'

def test_delete_budget(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    response = client.delete(f'/budgets/{budget_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['Message'] == 'Budget data Deleted Successfully.'
    response1 = client.get(f'/budgets/{budget_id}', headers=auth_headers)
    assert response1.status_code == 404

def test_budget_user_dependency(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}
    response = client.get(f'/budgets/{budget_id}', headers=userb_headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Budget data not Found.'

def test_user_cannot_update_other_users_budget(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}
    response = client.put(f'/budgets/{budget_id}', headers=userb_headers, json = {'month' : 8, "year" : 2026, 'limit_amount' : '34000'})
    assert response.status_code == 404
    assert response.json()['detail'] == 'Budget data not Found.'

def test_user_cannot_delete_other_users_budget(client, auth_headers, test_budgets):
    budget_id = test_budgets['id']
    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}
    response = client.delete(f'/budgets/{budget_id}', headers=userb_headers)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Budget data not Found.'
    response1 = client.get(f'/budgets/{budget_id}', headers=auth_headers)
    assert response1.status_code == 200

def test_budget_summary_under_limit(client, auth_headers, test_budgets, test_category, test_expenses):
    budget_id = test_budgets['id']
    response = client.get(f'/budgets/{budget_id}/summary', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['total_spent'] == '100.00'
    assert data['remaining'] == '24900.00'
    assert data['budget_exceeded'] is False
    assert data['exceeded_by'] == '0'

    response1 = client.get('/budgets/100/summary', headers=auth_headers)
    assert response1.status_code == 404
    assert response1.json()["detail"] == "Budget data not Found."

def test_budget_summary_exceeded(client, auth_headers, test_budgets, test_category):
    budget_id = test_budgets['id']
    category_id = test_category['id']
    client.post("/expenses/", headers=auth_headers,
                                                       json = {
                                                           "title" : "Pizza",
                                                           "amount" : "30000",
                                                           "description" : "Pizza Bakery",
                                                           "expense_date" : "2026-08-25",
                                                           "category_id" : category_id
                                                       })
    response = client.get(f'/budgets/{budget_id}/summary', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data['total_spent'] == '30000.00'
    assert data['remaining'] == '-5000.00'
    assert data['budget_exceeded'] is True
    assert data['exceeded_by'] == '5000.00'

def test_budget_within_warning(client, auth_headers, test_budgets, test_category, test_expenses):
    category_id = test_category['id']
    response = client.post("/expenses/", headers=auth_headers,
                                                           json = {
                                                               "title" : "Pizza",
                                                               "amount" : "14900",
                                                               "description" : "Pizza Bakery",
                                                               "expense_date" : "2026-08-25",
                                                               "category_id" : category_id
                                                           })
    assert response.status_code == 201
    assert "expense" in response.json()
    data = response.json()['budget_warning']
    assert data['exceeded'] is False
    assert data['exceeded_by'] == '0'

def test_budget_exceeds_warning(client, auth_headers, test_budgets, test_category, test_expenses):
    category_id = test_category['id']
    response = client.post("/expenses/", headers=auth_headers,
                                                           json = {
                                                               "title" : "Pizza",
                                                               "amount" : "29900",
                                                               "description" : "Pizza Bakery",
                                                               "expense_date" : "2026-08-25",
                                                               "category_id" : category_id
                                                           })
    assert response.status_code == 201
    assert "expense" in response.json()
    data = response.json()['budget_warning']
    assert data['exceeded'] is True
    assert data['exceeded_by'] == '5000.00'