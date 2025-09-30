import sys, os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import app
from database import engine, init_db, SQLModel

client = TestClient(app.app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    SQLModel.metadata.drop_all(engine)
    init_db()
    yield
    SQLModel.metadata.drop_all(engine)

def test_get_questions_hides_is_correct():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "2+2?",
        "qtype": "single",
        "options": [
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False},
        ],
    }
    client.post(f"/quizzes/{quiz_id}/questions", json=payload)
    res = client.get(f"/quizzes/{quiz_id}/questions")
    assert res.status_code == 200
    data = res.json()
    for opt in data[0]["options"]:
        assert "is_correct" not in opt

