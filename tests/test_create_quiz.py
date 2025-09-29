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


def test_create_quiz_success():
    res = client.post("/quizzes", json={"title": "My Quiz"})
    assert res.status_code == 201
    data = res.json()
    assert "id" in data and data["title"] == "My Quiz"

def test_create_quiz_empty_title_fails():
    res = client.post("/quizzes", json={"title": ""})
    assert res.status_code == 422
