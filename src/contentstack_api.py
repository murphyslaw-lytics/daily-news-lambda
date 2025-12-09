import os
import json
import requests
from utils import log, get_secret

# Contentstack constants
CONTENTSTACK_API_BASE = "https://api.contentstack.io/v3"
CONTENT_TYPE = "daily_news_article"

STACK_API_KEY = get_secret(os.environ.get("CONTENTSTACK_API_KEY"))
MANAGEMENT_TOKEN = get_secret(os.environ.get("CS_MGMT_TOKEN_SECRET"))

ENVIRONMENT = "main"
LOCALE = "en-us"

HEADERS = {
    "api_key": STACK_API_KEY,
    "authorization": MANAGEMENT_TOKEN,
    "Content-Type": "application/json"
}

# ----------------------------------------------------------
# DEDUPE — check if entry exists by URL
# ----------------------------------------------------------
def entry_exists(url):
    query = {"url": url}

    response = requests.get(
        f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries",
        headers=HEADERS,
        params={"query": json.dumps(query)}
    )

    if response.status_code != 200:
        log(f"[WARN] Could not check existing entries: {response.text}")
        return False

    data = response.json()
    entries = data.get("entries", [])

    exists = len(entries) > 0
    if exists:
        log(f"[SKIP] Already exists → {url}")

    return exists


# ----------------------------------------------------------
# PUBLISH ENTRY
# ----------------------------------------------------------
def publish_entry(uid):
    publish_url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries/{uid}/publish"

    payload = {
        "entry": {
            "environments": [ENVIRONMENT],
            "locales": [LOCALE]
        }
    }

    response = requests.post(publish_url, headers=HEADERS, json=payload)

    if not response.ok:
        log(f"[ERROR] Failed to publish entry {uid}: {response.text}")
        return False

    log(f"[PUBLISHED] Entry UID: {uid}")
    return True


# ----------------------------------------------------------
# MAIN INGESTION PIPELINE
# ----------------------------------------------------------
def process_articles(articles):
    created = 0
    skipped = 0
    published = 0

    for article in articles:
        title = article.get("title")
        url = article.get("url")

        # Missing URL → cannot dedupe → skip
        if not url:
            log(f"[SKIP] Missing URL → {title}")
            skipped += 1
            continue

        # Check for duplicates
        if entry_exists(url):
            skipped += 1
            continue

        # Build entry payload
        entry_data = {
            "entry": {
                "headline": title,
                "url": url,
                "source": article.get("source"),
                "summary": article.get("summary"),
                "thumbnail_url": article.get("thumbnail_url"),
                "published_at": article.get("published_at"),
                "run_date": article.get("run_date"),
            }
        }

        log(f"[CREATE] Creating entry: {title}")

        # Create entry
        create_url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries"
        response = requests.post(create_url, headers=HEADERS, json=entry_data)

        if not response.ok:
            log(f"[ERROR] Entry creation failed: {response.text}")
            continue

        entry_uid = response.json()["entry"]["uid"]
        created += 1

        # Auto-publish
        if publish_entry(entry_uid):
            published += 1

    return {
        "created": created,
        "skipped": skipped,
        "published": published
    }
