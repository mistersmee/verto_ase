from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from pydantic import BaseModel, constr
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session

DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(DATABASE_URL, echo=False)

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

class QuizCreate(BaseModel):
    title: constr(min_length=1)

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


# Simple health endpoint
@app.get("/health")
def health():
    return {"status": "ok"}
