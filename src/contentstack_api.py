import os
import requests
from utils import log, get_secret

# Contentstack constants
CONTENTSTACK_API_BASE = "https://api.contentstack.io/v3"
CONTENT_TYPE = "daily_news_article"

# Environment variables from Lambda
STACK_API_KEY = get_secret(os.environ.get("CONTENTSTACK_API_KEY"))
MANAGEMENT_TOKEN = get_secret(os.environ.get("CS_MGMT_TOKEN_SECRET"))

def publish_articles(articles):
    url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries"

    headers = {
        "api_key": STACK_API_KEY,
        "authorization": MANAGEMENT_TOKEN,
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

        results.append(response.json())

    return {"created": len(results)}
