import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from dotenv import load_dotenv
import os

load_dotenv()

DB_PWD = os.getenv('DB_PWD')

TEST_DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('TEST_DB_NAME')}"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit = False)

@pytest.fixture(scope='session', autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())

    db.commit()

    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def test_user(client):
    data = {
        "username" : "testuser",
        "email" : "test@example.com",
        "password" : "TestPassword123"
    }
    response = client.post('/users/', json=data)

    assert response.status_code == 201

    return response.json()

@pytest.fixture
def auth_headers(client, test_user):
    data = {
        "username" : test_user["username"],
        "password" : "TestPassword123"
    }
    response = client.post("/auth/login", data = data)

    assert response.status_code == 200
    token = response.json()["access_token"]
    return {
        "Authorization" : f"Bearer {token}"
    }

@pytest.fixture
def test_category(client):
    response = client.post("/categories/", json = {"name" : "Food"})
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def test_expenses(client, auth_headers, test_category):
    cat_id = test_category["id"]
    response = client.post("/expenses/", headers=auth_headers,
                               json = {
                                   "title" : "Dinner",
                                   "amount" : "100",
                                   "description" : "Dinner",
                                   "expense_date" : "2026-08-11",
                                   "category_id" : cat_id
                               })
    assert response.status_code == 201
    return response.json()
@pytest.fixture
def test_budgets(client, auth_headers):
    response = client.post('/budgets/', headers=auth_headers,
                           json={
                               "month" : 8,
                               "year" : 2026,
                               "limit_amount" : "25000"
                           })
    assert response.status_code == 201
    return response.json()