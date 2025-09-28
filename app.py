from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, constr, field_validator
from typing import List, Optional
from sqlmodel import SQLModel, Field, create_engine, Session
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

# Simple health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
