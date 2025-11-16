from database import SessionLocal, Quiz
from scraper import scrape_wikipedia
from datetime import datetime
import json

def test_scrape_and_store(url: str):
    # Step 1: Scrape Wikipedia
    print(f"🔍 Scraping article: {url}")
    title, text = scrape_wikipedia(url)
    print(f"✅ Scraped Title: {title[:50]}...")

    # Step 2: Create DB session
    db = SessionLocal()

    try:
        # Step 3: Create new Quiz entry
        new_quiz = Quiz(
            url=url,
            title=title,
            date_generated=datetime.utcnow(),
            scraped_content=text,
            full_quiz_data=json.dumps({"article": title, "summary": text[:500]})
        )

        # Step 4: Add and commit
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)

        print(f"✅ Successfully saved to DB with ID: {new_quiz.id}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_url = input("Enter Wikipedia URL: ").strip()
    test_scrape_and_store(test_url)
