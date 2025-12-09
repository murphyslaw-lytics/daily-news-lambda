import os
import requests
from utils import log

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"

def fetch_news(api_key):
    """
    Fetch top articles using NewsAPI.org.
    You can tune queries / sources / languages as you like.
    """

    query = "personalization OR \"data orchestration\" OR \"customer experience\" OR martech OR CDP"

    params = {
        "q": query,
        "language": "en",
        "pageSize": 10,
        "sortBy": "publishedAt",
    }

    headers = {
        "X-Api-Key": api_key
    }

    log(f"[NewsAPI] Calling {NEWSAPI_ENDPOINT} with query: {query}")
    response = requests.get(NEWSAPI_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "summary": item.get("description") or "",
            "published_at": item.get("publishedAt"),
            "source": (item.get("source") or {}).get("name"),
            "author": item.get("author")
        })

    log(f"[NewsAPI] Fetched {len(articles)} articles")
    return articles
