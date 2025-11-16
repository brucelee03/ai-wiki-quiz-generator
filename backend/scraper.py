import requests # type: ignore
from bs4 import BeautifulSoup # type: ignore

def scrape_wikipedia(url: str):
    # 1 Fetch the page with a user-agent
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AIWikiBot/1.0)"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")

    # 2 Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 3 Extract title safely
    title_tag = soup.find("h1", id="firstHeading")
    title = title_tag.text.strip() if title_tag else "Untitled"

    # 4 Find main content area
    content = soup.find("div", id="mw-content-text")
    if not content:
        raise Exception("Main content area not found.")

    # 5 Remove unwanted elements
    for tag in content.find_all(["sup", "table", "style", "script", "span"]): # type: ignore
        tag.decompose()

    # 6 Extract text
    cleaned_text = content.get_text(separator="\n", strip=True)

    return title, cleaned_text


if __name__ == "__main__":
    url = input("Enter a Wikipedia URL: ").strip()
    if not url.startswith("http"):
        print("⚠️ Please enter a valid URL (e.g., https://en.wikipedia.org/wiki/Python_(programming_language))")
    else:
        title, text = scrape_wikipedia(url)
        print(f"\nTitle: {title}\n")
        print(f"Text sample:\n{text[:500]}...")
