from fastapi.routing import websocket_session
from httpx import options
import pytest
from fastapi.testclient import TestClient
import sys, os

from sqlalchemy.sql.operators import op
from sqlalchemy.util import wrap_callable

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app, engine, SQLModel

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

def test_submit_answers_single_choice_correct_and_incorrect():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "2+2?",
        "qtype": "single",
        "options": [
            {"text": "4", "is_correct": "True"},
            {"text": "5", "is_correct": "False"},
        ],
    }
    q_res = client.post(f"/quizzes/{quiz_id}/questions", json=payload).json()
    qid = q_res["id"]
    opts = q_res["options"]
    correct_id = opts[0]["id"]

    # Correct answer
    submission = {"answers": [{"question_id": qid, "selected_option_ids": correct_id}]}
    res = client.post(f"/quizzes/{quiz_id}/submit", json=submission)
    assert res.json()["score"] == 1

    # Incorrect answer
    wrong_id = opts[1]["id"]
    submission = {"answers": [{"question_id": qid, "selected_option_ids": wrong_id}]}
    res = client.post(f"/quizzes/{quiz_id}/submit", json=submission)
    assert res.json()["score"] == 0

def test_submit_answers_text_question():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {"text": "Explain gravity", "qtype": "text"}
    q_res = client.post(f"/quizzes/{quiz_id}/questions", json=payload).json()
    qid = q_res["id"]
    submission = {"answers": [{"question_id": qid, "text_answer": "It pulls objects"}]}
    res = client.post(f"/quizzes/{quiz_id}/submit", json=submission)
    assert res.json()["score"] == 1

def test_submit_answers_multiple_choice():
    quiz_id = client.post("/quizzes", json={"title": "Qz"}).json()["id"]
    payload = {
        "text": "Select primes",
        "qtype": "multiple",
        "options": [
            {"text": "2", "is_correct": "True"},
            {"text": "3", "is_correct": "True"},
            {"text": "4", "is_correct": "False"},
        ],
    }
    q_res = client.post(f"/quizzes/{quiz_id}/questions", json=payload).json()
    qid = q_res["id"]
    opts = q_res["options"]
    correct_ids = [opt["id"] for opt in q_res["options"][:2]]
    wrong_id = opts[2]["id"]

    print(opts)
    print(correct_ids)
    print(wrong_id)

    # Exact correct set
    submission = {"answers": [{"question_id": qid, "selected_option_ids": correct_ids}]}
    res = client.post(f"/quizzes/{quiz_id}/submit", json=submission)
    assert res.json()["score"] == 1

    # Wrong answer
    submission = {"answers": [{"question_id": qid, "selected_option_ids": 3}]}
    res = client.post(f"/quizzes/{quiz_id}/submit", json=submission)
    assert res.json()["score"] == 0
