from typing import Optional
from enum import Enum
from sqlmodel import SQLModel, Field

class QuestionType(str, Enum):
    single = "single"
    multiple = "multiple"
    text = "text"

class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

class Question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    text: str
    qtype: QuestionType = Field(default=QuestionType.single)

class Option(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="question.id")
    text: str
    is_correct: bool = Field(default=False)
