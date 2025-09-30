from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./quiz.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)
