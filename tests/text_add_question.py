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

def test_add_single_choice_question_success():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "2+2?",
        "qtype": "single",
        "options": [
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False},
        ],
    }
    res = client.post(f"/quizzes/{quiz_id}/questions", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["qtype"] == "single"
    assert len(data["options"]) == 2

def test_add_single_choice_with_multiple_correct_fails():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "2+3?",
        "qtype": "single",
        "options": [
            {"text": "5", "is_correct": True},
            {"text": "6", "is_correct": True},
        ],
    }
    res = client.post(f"/quizzes/{quiz_id}/questions", json=payload)
    assert res.status_code == 422

def test_add_multiple_choice_requires_at_least_one_correct():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "Select primes",
        "qtype": "multiple",
        "options": [
            {"text": "4", "is_correct": False},
            {"text": "6", "is_correct": False},
        ],
    }
    res = client.post(f"/quizzes/{quiz_id}/questions", json=payload)
    assert res.status_code == 422

def test_add_text_question_with_options_fails():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "Explain gravity",
        "qtype": "text",
        "options": [{"text": "irrelevant", "is_correct": False}],
    }
    res = client.post(f"/quizzes/{quiz_id}/questions", json=payload)
    assert res.status_code == 422
