from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, constr, field_validator
from typing import List, Optional
from sqlalchemy.orm.interfaces import ORMOption
from sqlmodel import SQLModel, Field, create_engine, Session, select
from enum import Enum

DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(DATABASE_URL, echo=False)

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

class QuizCreate(BaseModel):
    title: constr(min_length=1)

class Option(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    text: str
    is_correct: bool = Field(default=False)

class OptionCreate(BaseModel):
    text: constr(min_length=1)
    is_correct: bool = False

class QuestionType(str, Enum):
    single = "single"
    multiple = "multiple"
    text = "text"

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id : int = Field(foreign_key="quiz.id")
    text: str
    qtype: QuestionType = Field(default=QuestionType.single)

class QuestionCreate(BaseModel):
    text: constr(min_length=1)
    qtype: QuestionType
    options: Optional[List[OptionCreate]] = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, values):
        qtype = values.data.get("qtype")
        if qtype in (QuestionType.single, QuestionType.multiple):
            if not v or len(v) < 2:
                raise ValueError("Choice questions must have at least 2 options")
            correct_count = sum(1 for o in v if o.is_correct)
            if qtype == QuestionType.single and correct_count != 1:
                raise ValueError("Single choice must have exactly 1 correct option")
            if qtype == QuestionType.multiple and correct_count < 1:
                raise ValueError("Multiple choice must have at least 1 correct option")
        else:
            if v and len(v) > 0:
                raise ValueError("Text questions must not include options")
        return v

class PublicOption(BaseModel):
    id: int
    text: str

class PublicQuestion(BaseModel):
    id: int
    text: str
    qtype: QuestionType
    options: Optional[List[PublicOption]] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan, title="Verto ASE Challenge")

@app.post("/quizzes", status_code=status.HTTP_201_CREATED)
def create_quiz(payload: QuizCreate):
    quiz = Quiz(title=payload.title)
    with Session(engine) as session:
        session.add(quiz)
        session.commit()
        session.refresh(quiz)
    return {"id": quiz.id, "title": quiz.title}

@app.post("/quizzes/{quiz_id}/questions", status_code=status.HTTP_201_CREATED)
def add_question(quiz_id: int, payload: QuestionCreate):
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        question = Question(quiz_id=quiz_id, text=payload.text, qtype=payload.qtype)
        session.add(question)
        session.commit()
        session.refresh(question)
        created_options = []
        if payload.options:
            for opt in payload.options:
                option = Option(question_id = question.id, text = opt.text, is_correct=opt.is_correct)
                session.add(option)
                session.commit()
                session.refresh(option)
                created_options.append({"id": option.id, "text": option.text, "is_correct": option.is_correct})
        return {
            "id": question.id,
            "text": question.text,
            "qtype": question.qtype,
            "options": created_options
        }

@app.get("/quizzes/{quiz_id}/questions", response_model=List[PublicQuestion])
def get_questions(quiz_id: int):
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        questions = session.exec(select(Question).where(Question.quiz_id == quiz_id)).all()
        output = []
        for q in questions:
            opts = session.exec(select(Option).where(Option.question_id == q.id)).all()
            if q.qtype == QuestionType.text:
                output.append({"id": q.id, "text": q.text, "qtype": q.qtype, "options": None})
            else:
                public_opts = [{"id": o.id, "text": o.text} for o in opts]
                output.append({"id": q.id, "text": q.text, "qtype": q.qtype, "options": public_opts})
        return output

@app.get("/quizzes")
def list_quizzes():
    with Session(engine) as session:
        quizzes = session.exec(select(Quiz)).all()
        result = []
        for q in quizzes:
            ques = session.exec(select(Question).where(Question.quiz_id == q.id)).all()
            result.append({"id": q.id, "title": q.title, "question_count": len(ques)})
        return result

@app.post("/quizzes/{quiz_id}/submit")
def submit_answers(quiz_id: int, submission: dict):
    with Session(engine) as session:
        quiz = session.get(Quiz, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        answers = submission.get("answers", [])
        if not isinstance(answers, list):
            raise HTTPException(status_code=400, detail="Answers must be a list")

        ques = session.exec(select(Question).where(Question.quiz_id == quiz.id)).all()
        total = len(ques)
        score = 0

        for ans in answers:
            q_id = ans.get("question_id")
            selected_option_ids = ans.get("selected_option_ids", [])
            question = session.get(Question, q_id)
            if not question or question.quiz_id != quiz_id:
                continue

            if question.qtype == "single":
                correct_options = session.exec(select(Option).where(Option.question_id == q_id, Option.is_correct == True)).all()
                correct_ids = sorted([o.id for o in correct_options])

                if selected_option_ids == correct_ids[0]:
                    score += 1

            elif question.qtype == "text":
                if ans.get("text_answer") and len(ans.get("text_answer")) <= 300:
                    score += 1

            elif question.qtype == "multiple":

                if isinstance(selected_option_ids, int):
                    selected_option_ids = [selected_option_ids]

                selected_option_ids = set(selected_option_ids)

                correct_options = session.exec(select(Option).where(Option.question_id == q_id, Option.is_correct == True)).all()
                correct_ids = sorted([o.id for o in correct_options])

                correct_ids = set(selected_option_ids)

                if selected_option_ids.issubset(correct_ids):
                    score += 1

        return {"score": score, "total": total}

# Simple health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
