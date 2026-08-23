def test_create_expenses(client, auth_headers, test_category, test_expenses):
    cat_id = test_category["id"]
    data = test_expenses
    assert "expense" in data
    assert "budget_warning" in data
    expense_data = data["expense"]
    assert expense_data["title"] == "Dinner"
    assert expense_data["category_id"] == cat_id
    assert expense_data["amount"] == "100.00"
    assert data["budget_warning"] is None

def test_invalid_expense_category(client, auth_headers):
    response = client.post("/expenses/", headers=auth_headers,
                           json = {
                               "title" : "Dinner",
                               "amount" : "100",
                               "description" : "Dinner",
                               "expense_date" : "2026-08-11",
                               "category_id" : 1
                           })
    assert response.status_code == 404
    assert response.json()['detail'] == 'Category does not exist.'

def test_get_expenses(client, auth_headers, test_category, test_expenses):
    cat_id = test_category["id"]
    response2 = client.post("/expenses/", headers=auth_headers,
                               json = {
                                   "title" : "Lunch",
                                   "amount" : "100",
                                   "description" : "Lunch",
                                   "expense_date" : "2026-08-15",
                                   "category_id" : cat_id
                               })
    assert response2.status_code == 201

    response = client.get('/expenses/', headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    title = [expense["title"] for expense in data]
    assert "Dinner" in title
    assert "Lunch" in title

def test_user_can_only_see_own_expenses(client, auth_headers, test_category, test_expenses):
    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}

    cat_id = test_category["id"]
    response1 = client.post("/expenses/", headers=userb_headers,
                                   json = {
                                       "title" : "Lunch",
                                       "amount" : "100",
                                       "description" : "Lunch",
                                       "expense_date" : "2026-08-15",
                                       "category_id" : cat_id
                                   })
    assert response1.status_code == 201

    user1_response = client.get('/expenses/', headers=auth_headers)
    user2_response = client.get('/expenses/', headers=userb_headers)

    assert user1_response.status_code == 200
    assert user2_response.status_code == 200
    user1 = [expense['title'] for expense in user1_response.json()]
    user2 = [expense['title'] for expense in user2_response.json()]
    assert "Dinner" in user1
    assert "Lunch" not in user1
    assert "Lunch" in user2
    assert "Dinner" not in user2

def test_get_expense_by_id(client, auth_headers, test_category, test_expenses):
    cat_id = test_category["id"]
    expense_id = test_expenses["expense"]["id"]

    response = client.get(f"/expenses/{expense_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == expense_id
    assert data["title"] == "Dinner"
    assert data["category_id"] == cat_id

def test_user_cannot_get_other_user_expenses(client, test_expenses):
    expense_id = test_expenses["expense"]["id"]

    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}

    response = client.get(f"/expenses/{expense_id}", headers=userb_headers)
    assert response.status_code == 404
    assert response.json()['detail'] == "Expense does not exist."

def test_update_expense(client, auth_headers, test_category, test_expenses):
    expense_id = test_expenses['expense']['id']
    category_id = test_category['id']

    response = client.put(f'/expenses/{expense_id}', headers=auth_headers,
                          json = {
                              "title" : "Pasteries",
                              "amount" : "250.00",
                              "description" : "desserts",
                              "expense_date" : "2026-08-21",
                              "category_id" : category_id
                          })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Pasteries"
    assert data["amount"] == "250.00"
    assert data["description"] == "desserts"
    assert data["expense_date"] == "2026-08-21"
    assert data["category_id"] == category_id

def test_invalid_update_expense(client, test_expenses, auth_headers):
    expense_id = test_expenses['expense']['id']
    
    response = client.put(f'/expenses/{expense_id}', headers=auth_headers,
                            json = {
                                "title" : "Pasteries",
                                "amount" : "250.00",
                                "description" : "desserts",
                                "expense_date" : "2026-08-21",
                                "category_id" : 9999
                            })
    assert response.status_code == 404
    assert response.json()['detail'] == "Category does not exist."

def test_delete_expense(client, test_expenses, auth_headers):
    expense_id = test_expenses['expense']['id']
        
    response = client.delete(f'/expenses/{expense_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json()['Message'] == 'Expense data Deleted Successfully.'

    response1 = client.get(f'/expenses/{expense_id}', headers=auth_headers)
    assert response1.status_code == 404
    assert response1.json()['detail'] == 'Expense does not exist.'

def test_user_cannot_update_others_expenses(client, test_category, test_expenses):
    expense_id = test_expenses['expense']['id']

    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}

    response = client.put(f'/expenses/{expense_id}', headers=userb_headers,
                                json = {
                                    "title" : "Pasteries",
                                    "amount" : "250.00",
                                    "description" : "desserts",
                                    "expense_date" : "2026-08-21",
                                    "category_id" : test_category["id"]
                                })

    assert response.status_code == 404
    assert response.json()['detail'] == "Expense Does not exist."

def test_other_user_cannot_delete(client, test_expenses):
    expense_id = test_expenses['expense']['id']

    client.post('/users/', json = {"username" : "userb", "email" : "userb@example.com", "password" : "TestPassword123"})
    login = client.post("/auth/login", data = {"username" : "userb", "password" : "TestPassword123"})
    userb_headers = {"Authorization" : f"Bearer {login.json()['access_token']}"}

    response = client.delete(f'/expenses/{expense_id}', headers=userb_headers)

    assert response.status_code == 404
    assert response.json()['detail'] == "Expense data not Found."

def test_expense_pagination(client, auth_headers, test_category, test_expenses):
    category_id = test_category['id']
    client.post("/expenses/", headers=auth_headers,
                                       json = {
                                           "title" : "Lunch",
                                           "amount" : "100",
                                           "description" : "Lunch",
                                           "expense_date" : "2026-08-15",
                                           "category_id" : category_id
                                       })

    response = client.get('/expenses/?skip=0&limit=2', headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert isinstance(data, list)

    response1 = client.get('/expenses/?skip=1&limit=2', headers=auth_headers)

    assert response1.status_code == 200
    data1 = response1.json()
    assert isinstance(data1, list)
    assert len(data1) == 1

def test_expense_category_filter(client, auth_headers, test_category, test_expenses):
    category_id = test_category['id']
    cat_response = client.post('/categories/', headers=auth_headers, json={"name" : "Travel"})
    cat_id = cat_response.json()["id"]
    exp_response = client.post('/expenses/', headers=auth_headers, 
                               json={
                                   "title" : "Goa",
                                   "amount" : "1234.00",
                                   "description" : "Family Trip",
                                   "expense_date" : "2026-06-11",
                                   "category_id" : cat_id
                               })
    assert exp_response.status_code == 201

    response = client.get(f'/expenses/?category_id={category_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    titles = [expense['title'] for expense in data]
    assert "Dinner" in titles
    assert "Goa" not in titles

def test_expense_date_filter(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                           json = {
                                               "title" : "Burger",
                                               "amount" : "100",
                                               "description" : "Truffles",
                                               "expense_date" : "2026-08-05",
                                               "category_id" : category_id
                                           })
    client.post("/expenses/", headers=auth_headers,
                                           json = {
                                               "title" : "Cake",
                                               "amount" : "100",
                                               "description" : "Dessert",
                                               "expense_date" : "2026-08-15",
                                               "category_id" : category_id
                                           })
    client.post("/expenses/", headers=auth_headers,
                                           json = {
                                               "title" : "Pizza",
                                               "amount" : "100",
                                               "description" : "Pizza Bakery",
                                               "expense_date" : "2026-08-25",
                                               "category_id" : category_id
                                           })

    response = client.get("/expenses/?start_date=2026-08-10&end_date=2026-08-20", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    dates = [expense["expense_date"] for expense in data]
    assert "2026-08-15" in dates
    assert "2026-08-05" not in dates
    assert "2026-08-05" not in dates

def test_invalid_expense_date_range(client, auth_headers, test_expenses):
    response = client.get("/expenses/?start_date=2026-08-20&end_date=2026-08-10", headers=auth_headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Start date cannot be after end date"

def test_expense_sortby_orderby(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                               json = {
                                                   "title" : "Burger",
                                                   "amount" : "299",
                                                   "description" : "Truffles",
                                                   "expense_date" : "2026-08-05",
                                                   "category_id" : category_id
                                               })
    client.post("/expenses/", headers=auth_headers,
                                               json = {
                                                   "title" : "Cake",
                                                   "amount" : "179",
                                                   "description" : "Dessert",
                                                   "expense_date" : "2026-08-15",
                                                   "category_id" : category_id
                                               })
    client.post("/expenses/", headers=auth_headers,
                                               json = {
                                                   "title" : "Pizza",
                                                   "amount" : "529",
                                                   "description" : "Pizza Bakery",
                                                   "expense_date" : "2026-08-25",
                                                   "category_id" : category_id
                                               })

    response = client.get('/expenses/?sort_by=amount&sort_order=asc', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    amounts = [float(expense["amount"]) for expense in data]
    assert amounts == sorted(amounts)

    response1 = client.get('/expenses/?sort_by=amount&sort_order=desc', headers=auth_headers)
    assert response1.status_code == 200
    data1 = response1.json()
    assert isinstance(data1, list)
    amounts1 = [float(expense["amount"]) for expense in data1]
    assert amounts1 == sorted(amounts1, reverse=True)

def test_expense_sortby_date(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                                   json = {
                                                       "title" : "Burger",
                                                       "amount" : "299",
                                                       "description" : "Truffles",
                                                       "expense_date" : "2026-08-05",
                                                       "category_id" : category_id
                                                   })
    client.post("/expenses/", headers=auth_headers,
                                                   json = {
                                                       "title" : "Cake",
                                                       "amount" : "179",
                                                       "description" : "Dessert",
                                                       "expense_date" : "2026-08-15",
                                                       "category_id" : category_id
                                                   })
    client.post("/expenses/", headers=auth_headers,
                                                   json = {
                                                       "title" : "Pizza",
                                                       "amount" : "529",
                                                       "description" : "Pizza Bakery",
                                                       "expense_date" : "2026-08-25",
                                                       "category_id" : category_id
                                                   })

    response = client.get('/expenses/?sort_by=expense_date&sort_order=asc', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    dates = [expense["expense_date"] for expense in data]
    assert dates == sorted(dates)

def test_invalid_expense_sortby(client, test_category, auth_headers):
    response = client.get('/expenses/?sort_by=banana', headers=auth_headers)
    assert response.status_code == 422

def test_expense_pagination_boundaries(client, auth_headers, test_expenses):
    response = client.get('/expenses/?limit=0', headers=auth_headers)
    assert response.status_code == 422
    response1 = client.get('/expenses/?skip=-1', headers=auth_headers)
    assert response.status_code == 422

def test_expense_summary(client, auth_headers, test_expenses, test_category):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                                       json = {
                                                           "title" : "Burger",
                                                           "amount" : "300",
                                                           "description" : "Truffles",
                                                           "expense_date" : "2026-08-05",
                                                           "category_id" : category_id
                                                       })
    client.post("/expenses/", headers=auth_headers,
                                                       json = {
                                                           "title" : "Cake",
                                                           "amount" : "180",
                                                           "description" : "Dessert",
                                                           "expense_date" : "2026-08-15",
                                                           "category_id" : category_id
                                                       })

    response = client.get('/expenses/summary', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_expense"] == 580.0
    assert data['expense_count'] == 3
    assert data["average_expense"] == 193.33333333333334

def test_monthly_expense_summary(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                                           json = {
                                                               "title" : "Burger",
                                                               "amount" : "300",
                                                               "description" : "Truffles",
                                                               "expense_date" : "2026-08-05",
                                                               "category_id" : category_id
                                                           })
    client.post("/expenses/", headers=auth_headers,
                                                           json = {
                                                               "title" : "Cake",
                                                               "amount" : "180",
                                                               "description" : "Dessert",
                                                               "expense_date" : "2026-07-15",
                                                               "category_id" : category_id
                                                           })

    response = client.get('/expenses/summary/?month=8', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_expense"] == 400.0
    assert data["expense_count"] == 2
    assert data["average_expense"] == 200.0

def test_yearly_expense(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                                               json = {
                                                                   "title" : "Burger",
                                                                   "amount" : "300",
                                                                   "description" : "Truffles",
                                                                   "expense_date" : "2025-06-05",
                                                                   "category_id" : category_id
                                                               })
    client.post("/expenses/", headers=auth_headers,
                                                               json = {
                                                                   "title" : "Cake",
                                                                   "amount" : "180",
                                                                   "description" : "Dessert",
                                                                   "expense_date" : "2026-07-15",
                                                                   "category_id" : category_id
                                                               })
    response = client.get('/expenses/summary/?year=2026', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_expense"] == 280.0
    assert data["expense_count"] == 2
    assert data["average_expense"] == 140.0

def test_month_and_year_expense_summary(client, auth_headers, test_category, test_expenses):
    category_id = test_category["id"]
    client.post("/expenses/", headers=auth_headers,
                                                                   json = {
                                                                       "title" : "Burger",
                                                                       "amount" : "300",
                                                                       "description" : "Truffles",
                                                                       "expense_date" : "2025-06-05",
                                                                       "category_id" : category_id
                                                                   })
    client.post("/expenses/", headers=auth_headers,
                                                                   json = {
                                                                       "title" : "Cake",
                                                                       "amount" : "180",
                                                                       "description" : "Dessert",
                                                                       "expense_date" : "2026-07-15",
                                                                       "category_id" : category_id
                                                                   })
    response = client.get('/expenses/summary/?month=8&year=2026', headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_expense"] == 100.0
    assert data["expense_count"] == 1
    assert data["average_expense"] == 100.0