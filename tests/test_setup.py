def test_database_connection(client):
    respone = client.get("/")

    assert respone.status_code == 200
    assert respone.json()["Message"] == "App running successfully"