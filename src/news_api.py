import requests
from utils import log, get_secret
import os

def fetch_top_articles():
    """
    Fetch top news articles using Bing News Search API.
    """
    api_key_secret = os.getenv("BING_NEWS_SECRET")
    api_key = get_secret(api_key_secret)

    import os

BING_ENDPOINT = os.environ.get("BING_ENDPOINT", "")  # new var from template

url = f"{BING_ENDPOINT}/bing/v7.0/news/search"

    query = "personalisation OR data orchestration OR AI OR customer experience"

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {
        "q": query,
        "count": 10,
        "sortBy": "Date"
    }

    log("Calling Bing News API...")
    resp = requests.get(endpoint, headers=headers, params=params)
    resp.raise_for_status()

    data = resp.json()
    articles = []

    for item in data.get("value", []):
        articles.append({
            "title": item.get("name"),
            "url": item.get("url"),
            "summary": item.get("description"),
            "published_at": item.get("datePublished")
        })

    log(f"Fetched {len(articles)} articles")
    return articles
