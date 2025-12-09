import os
import requests
from utils import log, get_secret

CONTENTSTACK_API_BASE = "https://api.contentstack.io/v3"
CONTENT_TYPE = "daily_news_article"

STACK_API_KEY = get_secret(os.environ.get("CONTENTSTACK_API_KEY"))
MANAGEMENT_TOKEN = get_secret(os.environ.get("CS_MGMT_TOKEN_SECRET"))

HEADERS = {
    "api_key": STACK_API_KEY,
    "authorization": MANAGEMENT_TOKEN,
    "Content-Type": "application/json"
}

ENVIRONMENT = "main"
LOCALE = "en-us"


# -------------------------------------------------------------
# Helper: Check if article already exists (Dedupe)
# -------------------------------------------------------------
def entry_exists(url):
    query = {
        "query": {
            "url": url
        }
    }

    response = requests.get(
        f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries",
        headers=HEADERS,
        params={"query": str(query)}
    )

    if response.status_code != 200:
        log(f"[WARN] Failed to check existing entries: {response.text}")
        return False

    data = response.json()
    return len(data.get("entries", [])) > 0


# -------------------------------------------------------------
# Helper: Publish entry
# -------------------------------------------------------------
def publish_entry(entry_uid):
    publish_url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries/{entry_uid}/publish"

    payload = {
        "entry": {
            "environments": [ENVIRONMENT],
            "locales": [LOCALE]
        }
    }

    resp = requests.post(publish_url, headers=HEADERS, json=payload)

    if resp.status_code >= 300:
        log(f"[ERROR] Failed to publish entry {entry_uid}: {resp.text}")
        return False

    return True


# -------------------------------------------------------------
# Main: Create entries with dedupe + automatic publishing
# -------------------------------------------------------------
def create_or_update_articles(articles):
    created = 0
    skipped = 0
    published = 0

    for article in articles:
        title = article.get("title")
        url = article.get("url")

        if not url:
            log(f"[SKIP] No URL → Cannot dedupe → Skipping: {title}")
            skipped += 1
            continue

        # 1. Dedupe check
        if entry_exists(url):
            log(f"[SKIP] Already exists → {url}")
            skipped += 1
            continue

        # 2. Build entry
        entry_data = {
            "entry": {
                "title": title,
                "url": url,
                "source": article.get("source"),
                "summary": article.get("summary"),
                "thumbnail_url": article.get("thumbnail_url"),
                "published_at": article.get("published_at"),
                "run_date": article.get("run_date"),
            }
        }

        log(f"[CREATE] Creating entry: {title}")

        # 3. Create entry
        create_url = f"{CONTENTSTACK_API_BASE}/content_types/{CONTENT_TYPE}/entries"
        response = requests.post(create_url, headers=HEADERS, json=entry_data)

        if not response.ok:
            log(f"[ERROR] Entry creation failed: {response.text}")
            continue

        entry_uid = response.json()["entry"]["uid"]
        created += 1

        # 4. Publish entry
        if publish_entry(entry_uid):
            log(f"[PUBLISHED] {title}")
            published += 1

    return {
        "created": created,
        "skipped": skipped,
        "published": published
    }
