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

def test_list_quizzes_and_question_count():
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
    res = client.get("/quizzes")
    assert res.status_code == 200
    quizzes = res.json()
    assert quizzes[0]["question_count"] == 1
