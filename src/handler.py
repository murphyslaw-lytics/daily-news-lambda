import os
from utils import log, get_secret
from news_api import fetch_news
from contentstack_api import process_articles

def lambda_handler(event, context):
    log("Daily News Lambda triggered")

    # Get Bing / News API Key
    secret_name = os.environ.get("BING_NEWS_SECRET")
    api_key = get_secret(secret_name)

    # Fetch articles from your news layer
    try:
        articles = fetch_news(api_key)
        log(f"[INFO] {len(articles)} articles fetched")
    except Exception as e:
        log(f"[ERROR] Failed to fetch news: {str(e)}")
        return {"statusCode": 500, "error": str(e)}

    # Process articles into Contentstack
    try:
        result = process_articles(articles)
        return {
            "statusCode": 200,
            "message": "Success",
            **result
        }
    except Exception as e:
        log(f"[ERROR] Contentstack ingestion failed: {str(e)}")
        return {"statusCode": 500, "error": str(e)}
