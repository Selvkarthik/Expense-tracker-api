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