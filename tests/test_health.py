import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, engine, SQLModel

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
