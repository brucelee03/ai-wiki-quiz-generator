# database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# 1 Create Database Connection URL
DATABASE_URL = "mysql+mysqlconnector://root:Jarvis#6.62607015@localhost/quiz_app"

# 2 Create the SQLAlchemy Engine
engine = create_engine(DATABASE_URL, echo=True)

# 3 Create Base Class
Base = declarative_base()

# 4 Define the Quiz Model
class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    date_generated = Column(DateTime, default=datetime.utcnow)
    scraped_content = Column(Text)
    full_quiz_data = Column(Text)

# 5 Create the Database Table
Base.metadata.create_all(bind=engine)

# 6 Create a Session Factory (used later for CRUD operations)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 7 Dependency - Get DB Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
