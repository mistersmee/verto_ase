from typing import List, Optional
from pydantic import BaseModel, constr, field_validator
from models import QuestionType

class QuizCreate(BaseModel):
    title: constr(min_length=1)

class OptionCreate(BaseModel):
    text: constr(min_length=1)
    is_correct: bool = False

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
