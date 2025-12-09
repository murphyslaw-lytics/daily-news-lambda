import os
from utils import log, get_secret
from news_api import fetch_news
from contentstack_api import create_or_update_articles

def lambda_handler(event, context):
    log("Daily News Lambda triggered")

    # Get secret for Bing or NewsAPI
    secret_name = os.environ.get("BING_NEWS_SECRET")
    api_key = get_secret(secret_name)

    # Fetch news
    try:
        articles = fetch_news(api_key)
    except Exception as e:
        log(f"[ERROR] Fetching news failed: {str(e)}")
        return {"statusCode": 500, "error": str(e)}

    # Publish to Contentstack
    try:
        result = create_or_update_articles(articles)
        return {
            "statusCode": 200,
            "message": "Success",
            "processed": len(articles),
            "created": result["created"],
            "skipped": result["skipped"],
            "published": result["published"]
        }
    except Exception as e:
        log(f"[ERROR] Contentstack failure: {str(e)}")
        return {"statusCode": 500, "error": str(e)}
