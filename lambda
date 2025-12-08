import os
import json
import logging
from datetime import datetime, timezone

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# --- External APIs ---
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/news/search"
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# --- Environment variables (configure in Lambda) ---
BING_API_KEY = os.environ["BING_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

CS_API_KEY = os.environ["CS_API_KEY"]
CS_MANAGEMENT_TOKEN = os.environ["CS_MANAGEMENT_TOKEN"]
CS_ENVIRONMENT = os.environ["CS_ENVIRONMENT"]          # e.g. "production"
CS_CONTENT_TYPE_UID = os.environ["CS_CONTENT_TYPE_UID"]  # e.g. "daily_news_article"
CS_REGION = os.environ.get("CS_REGION", "eu")          # "eu" or "na"

# Base URL depends on region
if CS_REGION == "eu":
    CS_BASE_URL = "https://eu-api.contentstack.com"
else:
    CS_BASE_URL = "https://api.contentstack.io"

NEWS_QUERY = os.environ.get(
    "NEWS_QUERY",
    "personalisation OR personalization OR "
    "\"customer experience\" OR \"customer data platform\" OR "
    "\"data orchestration\" OR \"CDP\" OR "
    "\"artificial intelligence\" OR \"machine learning\" OR \"generative ai\""
)

def fetch_bing_articles():
    """Fetch top recent articles from Bing News related to our query."""
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {
        "q": NEWS_QUERY,
        "count": 25,
        "mkt": "en-GB",
        "sortBy": "Date"
    }

    logger.info("Fetching articles from Bing News...")
    resp = requests.get(BING_ENDPOINT, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    articles = data.get("value", [])
    logger.info("Fetched %d articles from Bing", len(articles))
    return articles


def summarise_articles_with_openai(articles, max_items=10):
    """Use OpenAI to summarise each article in 2 sentences."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    summarised = []
    for article in articles[:max_items]:
        title = article.get("name", "")
        description = article.get("description", "") or ""
        url = article.get("url")
        provider = (article.get("provider") or [{}])[0].get("name", "Unknown")
        published = article.get("datePublished")
        thumb = (article.get("image") or {}).get("thumbnail", {}).get("contentUrl")

        prompt = (
            "You are helping a martech thought leader curate a daily list of articles "
            "for a website about personalisation, customer data, data orchestration, and AI.\n\n"
            f"Title: {title}\n"
            f"Description: {description}\n\n"
            "Write a 2–3 sentence summary focusing on why this is relevant for:\n"
            "- customer experience / personalisation\n"
            "- customer data platforms / data orchestration\n"
            "- AI / machine learning in marketing.\n"
            "Keep it non-salesy and suitable for a professional audience."
        )

        payload = {
            "model": "gpt-4.1-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 200,
        }

        logger.info("Summarising article with OpenAI: %s", title)
        r = requests.post(OPENAI_ENDPOINT, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        resp_data = r.json()
        summary = resp_data["choices"][0]["message"]["content"].strip()

        summarised.append({
            "title": title,
            "url": url,
            "source": provider,
            "published_at": published,
            "thumbnail_url": thumb,
            "summary": summary,
        })

    logger.info("Summarised %d articles with OpenAI", len(summarised))
    return summarised


# ---------- Contentstack helpers ----------

def cs_headers():
    return {
        "api_key": CS_API_KEY,
        "authorization": CS_MANAGEMENT_TOKEN,
        "Content-Type": "application/json",
    }

def find_existing_entry_by_url(url):
    """Check if an entry already exists for this URL."""
    query = json.dumps({"url": url})
    params = {"query": query}
    url_ = f"{CS_BASE_URL}/v3/content_types/{CS_CONTENT_TYPE_UID}/entries"
    r = requests.get(url_, headers=cs_headers(), params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    entries = data.get("entries", [])
    if entries:
        return entries[0]["uid"]
    return None

def create_entry(article, run_date_str):
    """Create a new Contentstack entry for a news article."""
    body = {
        "entry": {
            "title": article["title"],
            "url": article["url"],
            "source": article["source"],
            "summary": article["summary"],
            "thumbnail_url": article["thumbnail_url"],
            "run_date": run_date_str,
            "published_at": article["published_at"],
        }
    }

    url_ = f"{CS_BASE_URL}/v3/content_types/{CS_CONTENT_TYPE_UID}/entries"
    r = requests.post(url_, headers=cs_headers(), json=body, timeout=20)
    r.raise_for_status()
    return r.json()["entry"]["uid"]

def update_entry(entry_uid, article, run_date_str):
    """Update an existing Contentstack entry for this URL."""
    body = {
        "entry": {
            "title": article["title"],
            "source": article["source"],
            "summary": article["summary"],
            "thumbnail_url": article["thumbnail_url"],
            "run_date": run_date_str,
            "published_at": article["published_at"],
        }
    }

    url_ = f"{CS_BASE_URL}/v3/content_types/{CS_CONTENT_TYPE_UID}/entries/{entry_uid}"
    r = requests.put(url_, headers=cs_headers(), json=body, timeout=20)
    r.raise_for_status()
    return r.json()["entry"]["uid"]

def publish_entry(entry_uid, locale="en-us"):
    """Publish an entry to the configured environment."""
    body = {
        "entry": {
            "environments": [CS_ENVIRONMENT],
            "locales": [locale],
        }
    }
    url_ = f"{CS_BASE_URL}/v3/content_types/{CS_CONTENT_TYPE_UID}/entries/{entry_uid}/publish"
    r = requests.post(url_, headers=cs_headers(), json=body, timeout=20)
    r.raise_for_status()
    return True

def push_to_contentstack(articles):
    """Create/update & publish entries for all articles."""
    run_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    created_or_updated = []

    for article in articles:
        existing_uid = find_existing_entry_by_url(article["url"])
        if existing_uid:
            logger.info("Updating existing entry for URL: %s", article["url"])
            uid = update_entry(existing_uid, article, run_date_str)
        else:
            logger.info("Creating new entry for URL: %s", article["url"])
            uid = create_entry(article, run_date_str)

        publish_entry(uid)
        created_or_updated.append(uid)

    return created_or_updated


def lambda_handler(event, context):
    logger.info("Starting daily news Lambda run...")

    try:
        raw_articles = fetch_bing_articles()
        summarised = summarise_articles_with_openai(raw_articles, max_items=10)
        entry_uids = push_to_contentstack(summarised)

        logger.info("Successfully processed %d articles", len(entry_uids))
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Daily news update complete",
                "articles_published": len(entry_uids),
            })
        }

    except Exception as e:
        logger.exception("Error during daily news run")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
