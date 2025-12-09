import os
from utils import log, get_secret
from news_api import fetch_news
from contentstack_api import publish_articles

def lambda_handler(event, context):
    log("Daily News Lambda triggered")

    try:
        # 1. Get Bing key
        bing_secret_name = os.environ.get("BING_NEWS_SECRET")
        api_key = get_secret(bing_secret_name)
        articles = fetch_news(api_key)

        # 2. Fetch articles
        articles = fetch_news(bing_api_key)
        log(f"Fetched {len(articles)} articles from Bing")

        # 3. Publish to Contentstack
        results = publish_articles(articles)
        log(f"Published {len(results)} articles to Contentstack")

        return {
            "statusCode": 200,
            "message": "Success",
            "articles_processed": len(articles),
            "contentstack_result_count": len(results)
        }

    except Exception as e:
        log(f"ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "error": str(e)
        }
