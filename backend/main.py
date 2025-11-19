from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import json

from backend.database import engine, Base, Quiz, get_db
from backend.scraper import scrape_wikipedia
from backend.llm_quiz_generator import generate_quiz
from fastapi import Depends

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database connection failed: {e}. Server will start without creating tables.")

app = FastAPI()

# ---------------------------------------------------------
# CORS: Allow React Frontend
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# 1) POST /generate_quiz
# ---------------------------------------------------------
@app.post("/generate_quiz")
def generate_quiz_endpoint(payload: dict, db: Session = Depends(get_db)):
    """
    Accepts: { "url": "https://..." }
    Scrapes → Generates quiz → Saves to DB → Returns JSON.
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    # 1. Scrape text
    title, article_text = scrape_wikipedia(url)
    if not article_text:
        raise HTTPException(status_code=500, detail="Failed to scrape article.")

    # 2. Generate quiz
    quiz_data = generate_quiz(article_text)

    # 3. Save to database
    quiz_record = Quiz(
        url=url,
        title=quiz_data.title,
        full_quiz_data=json.dumps(quiz_data.dict()),
        date_generated=datetime.utcnow(),
    )

    db.add(quiz_record)
    db.commit()
    db.refresh(quiz_record)

    # 4. Return full quiz JSON
    return quiz_data.dict()


# ---------------------------------------------------------
# 2) GET /history
# ---------------------------------------------------------
@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    """
    Returns list of:
    { id, url, title, date_generated }
    """
    quizzes = db.query(Quiz).all()

    return [
        {
            "id": q.id,
            "url": q.url,
            "title": q.title,
            "date_generated": q.date_generated,
        }
        for q in quizzes
    ]


# ---------------------------------------------------------
# 3) GET /quiz/{quiz_id}
# ---------------------------------------------------------
@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """
    Fetches quiz record by ID and returns
    parsed JSON of full quiz data.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    # Convert JSON string → Python dict
    return json.loads(str(quiz.full_quiz_data))
