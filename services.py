from sqlmodel import Session, select
from models import Quiz, Question, Option, QuestionType

def create_quiz(session: Session, title: str) -> Quiz:
    quiz = Quiz(title=title)
    session.add(quiz)
    session.commit()
    session.refresh(quiz)
    return quiz

def add_question(session: Session, quiz_id: int, text: str, qtype: QuestionType, options: list = None):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        return None
    question = Question(quiz_id=quiz_id, text=text, qtype=qtype)
    session.add(question)
    session.commit()
    session.refresh(question)

    if options:
        for opt in options:
            option = Option(question_id=question.id, text=opt.text, is_correct=opt.is_correct)
            session.add(option)
        session.commit()
    return question

def list_quizzes(session: Session):
    quizzes = session.exec(select(Quiz)).all()
    result = []
    for q in quizzes:
        ques = session.exec(select(Question).where(Question.quiz_id == q.id)).all()
        result.append({"id": q.id, "title": q.title, "question_count": len(ques)})
    return result

def get_questions(session: Session, quiz_id: int):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        return None
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

def score_submission(session: Session, quiz_id: int, answers: list):
    quiz = session.get(Quiz, quiz_id)
    if not quiz:
        return None
    questions = session.exec(select(Question).where(Question.quiz_id == quiz.id)).all()
    total = len(questions)
    score = 0

    for ans in answers:
        q_id = ans.get("question_id")
        selected_option_ids = ans.get("selected_option_ids", [])
        question = session.get(Question, q_id)
        if not question or question.quiz_id != quiz_id:
            continue

        if question.qtype == QuestionType.single:
            correct_options = session.exec(select(Option).where(Option.question_id == q_id, Option.is_correct == True)).all()
            correct_ids = sorted([o.id for o in correct_options])

            if selected_option_ids == correct_ids[0]:
                score += 1

        elif question.qtype == QuestionType.multiple:
            if isinstance(selected_option_ids, int):
                selected_option_ids = [selected_option_ids]

            selected_option_ids = set(selected_option_ids)

            correct_options = session.exec(select(Option).where(Option.question_id == q_id, Option.is_correct == True)).all()
            correct_ids = sorted([o.id for o in correct_options])

            correct_ids = set(correct_ids)

            if selected_option_ids.issubset(correct_ids):
                score += 1


        elif question.qtype == QuestionType.text:
            if ans.get("text_answer") and len(ans.get("text_answer")) <= 300:
                score += 1

    return {"score": score, "total": total}
