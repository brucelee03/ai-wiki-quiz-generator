from datetime import datetime
from pydantic import BaseModel
from typing import List

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str

class QuizOutput(BaseModel):
    topic: str
    difficulty: str
    questions: List[QuizQuestion]

class Quiz(BaseModel):
    id: int
    url: str
    title: str
    date_generated: datetime
    scraped_content: str
    full_quiz_data: str