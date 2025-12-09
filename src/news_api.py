import os
import requests

def get_bing_endpoint():
    """
    Returns the Azure Cognitive Services endpoint without a trailing slash.
    """
    endpoint = os.environ.get("BING_ENDPOINT", "")
    if endpoint.endswith("/"):
        endpoint = endpoint[:-1]
    return endpoint

def fetch_news(api_key):
    """
    Fetches news articles using Azure Cognitive Services Bing News Search.
    """

    endpoint = get_bing_endpoint()
    url = "https://bing-news-search1.p.rapidapi.com/news/search"
    query = "personalisation OR data orchestration OR AI OR customer experience"

    params = {
        "q": query,
        "count": 10,
        "freshness": "Day",
        "textFormat": "Raw",
        "safeSearch": "Off"
    }

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "bing-news-search1.p.rapidapi.com"
    }
    
    print(f"[BING] Calling: {url}")
    response = requests.get(url, headers=headers, params=params)

    # Raise for HTTP errors
    response.raise_for_status()

    data = response.json()

    # Bing returns articles in data['value']
    return data.get("value", [])
