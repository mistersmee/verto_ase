from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session
from database import engine, init_db
from schemas import QuizCreate, QuestionCreate, PublicQuestion
from services import create_quiz, add_question, list_quizzes, get_questions, score_submission

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan, title="Verto ASE Challenge")

@app.post("/quizzes", status_code=status.HTTP_201_CREATED)
def create_quiz_route(payload: QuizCreate):
    with Session(engine) as session:
        quiz = create_quiz(session, payload.title)
        return {"id": quiz.id, "title": quiz.title}

@app.post("/quizzes/{quiz_id}/questions", status_code=status.HTTP_201_CREATED)
def add_question_route(quiz_id: int, payload: QuestionCreate):
    with Session(engine) as session:
        question = add_question(session, quiz_id, payload.text, payload.qtype, payload.options)
        if not question:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return {"id": question.id, "text": question.text, "qtype": question.qtype}

@app.get("/quizzes/{quiz_id}/questions", response_model=list[PublicQuestion])
def get_questions_route(quiz_id: int):
    with Session(engine) as session:
        questions = get_questions(session, quiz_id)
        if questions is None:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return questions

@app.get("/quizzes")
def list_quizzes_route():
    with Session(engine) as session:
        return list_quizzes(session)

@app.post("/quizzes/{quiz_id}/submit")
def submit_answers_route(quiz_id: int, submission: dict):
    with Session(engine) as session:
        result = score_submission(session, quiz_id, submission.get("answers", []))
        if result is None:
            raise HTTPException(status_code=404, detail="Quiz not found")
        return result

@app.get("/health")
def health():
    return {"status": "ok"}
