from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import SessionLocal, Quiz
from scraper import scrape_wikipedia
from datetime import datetime

app = FastAPI(title="AI Wiki Quiz Generator API")

# Pydantic model for request validation
class WikiRequest(BaseModel):
    url: str

@app.post("/scrape/")
def scrape_and_save(request: WikiRequest):
    try:
        # 1. Scrape the page
        title, text = scrape_wikipedia(request.url)

        # 2. Save to database
        db = SessionLocal()
        new_quiz = Quiz(
            url=request.url,
            title=title,
            date_generated=datetime.utcnow(),
            scraped_content=text,
            full_quiz_data={"article": title, "summary": text[:500]}
        )
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        db.close()

        # 3. Return response
        return {"id": new_quiz.id, "title": title, "preview": text[:300]}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
