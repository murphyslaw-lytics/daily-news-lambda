import os
from utils import log, get_secret
from news_api import fetch_news
from contentstack_api import publish_articles

def lambda_handler(event, context):
    log("Daily News Lambda triggered")

    # Get secret name from environment variable
    secret_name = os.environ.get("BING_NEWS_SECRET")
    if not secret_name:
        return {"statusCode": 500, "error": "BING_NEWS_SECRET env var not set"}

    log(f"Retrieving secret: {secret_name}")
    api_key = get_secret(secret_name)
    if not api_key:
        return {"statusCode": 500, "error": "Unable to retrieve API key"}

    # Fetch news using our NewsAPI wrapper
    try:
        articles = fetch_news(api_key)
    except Exception as e:
        log(f"Error fetching news: {str(e)}")
        return {"statusCode": 500, "error": str(e)}

    # Publish articles to Contentstack
    try:
        result = publish_articles(articles)
        return {
            "statusCode": 200,
            "message": "Success",
            "articles_processed": len(articles),
            "contentstack_result": result
        }
    except Exception as e:
        log(f"Contentstack ERROR: {str(e)}")
        return {"statusCode": 500, "error": str(e)}
