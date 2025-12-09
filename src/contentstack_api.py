import os
import requests
from utils import log

# Contentstack constants
CONTENTSTACK_API_BASE = "https://api.contentstack.io/v3"
CONTENT_TYPE = "daily_news_article"  # your real API ID

# Environment variables from Lambda
MANAGEMENT_TOKEN = os.environ.get("CONTENTSTACK_MANAGEMENT_TOKEN")
STACK_API_KEY = os.environ.get("CONTENTSTACK_API_KEY")

def publish_articles(articles):
    """
    Publish each article to Contentstack as an entry in daily_news_article.
    """

    url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries"

    headers = {
        "authorization": MANAGEMENT_TOKEN,
        "api_key": STACK_API_KEY,
        "Content-Type": "application/json",
        "X-Contentstack-Branch": "main",
        "X-Contentstack-Api-Version": "3.0"
}
 
    results = []

    for article in articles:
        entry = {
            "entry": {
                "title": article.get("title"),
                "url": article.get("url"),
                "source": article.get("source"),
                "summary": article.get("summary"),
                "thumbnail_url": article.get("thumbnail_url"),
                "published_at": article.get("published_at"),
                "run_date": article.get("run_date"),
            }
        }

        log(f"Creating entry: {entry['entry']['title']}")

        response = requests.post(url, headers=headers, json=entry)

        if not response.ok:
            log(f"Contentstack ERROR {response.status_code}: {response.text}")
            response.raise_for_status()

        data = response.json()
        results.append(data)

    return {"created": len(results)}
