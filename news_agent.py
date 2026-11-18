"""
news_agent.py - NewsAPI Integration
=====================================
Fetches the top 5 recent news articles about a competitor company
using the NewsAPI /everything endpoint. Handles missing keys,
rate limits, and network failures gracefully.
"""

import os
import requests
from datetime import datetime


def fetch_company_news(company_name: str, api_key: str = None) -> dict:
    """
    Fetches top 5 recent news articles for a company using NewsAPI.

    Args:
        company_name: Name of the competitor company.
        api_key: NewsAPI API Key. Falls back to NEWSAPI_API_KEY env var.

    Returns:
        dict with keys: success (bool), articles (list), error (str|None).
    """
    if not api_key:
        api_key = os.getenv("NEWSAPI_API_KEY")

    if not api_key or api_key.strip() == "":
        return {
            "success": False,
            "articles": [],
            "error": "NewsAPI key is missing. Please configure it to fetch competitor news."
        }

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'"{company_name}"',
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": 10,
        "apiKey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 401:
            return {
                "success": False, "articles": [],
                "error": "Unauthorized: Invalid NewsAPI key."
            }
        elif response.status_code == 429:
            return {
                "success": False, "articles": [],
                "error": "Rate limited: You have exceeded the NewsAPI request quota."
            }

        response.raise_for_status()
        data = response.json()

        if data.get("status") == "error":
            return {
                "success": False, "articles": [],
                "error": data.get("message", "Unknown API error from NewsAPI.")
            }

        raw_articles = data.get("articles", [])
        articles = []

        for art in raw_articles:
            if len(articles) >= 5:
                break

            title = art.get("title")
            if not title or "[Removed]" in title:
                continue

            # Parse publication date
            published_str = art.get("publishedAt", "")
            try:
                dt = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
                formatted_date = dt.strftime("%B %d, %Y")
            except Exception:
                formatted_date = published_str

            articles.append({
                "title": title,
                "source": art.get("source", {}).get("name", "Unknown Source"),
                "date": formatted_date,
                "description": art.get("description") or "No description available.",
                "url": art.get("url") or "#",
                "content": art.get("content") or ""
            })

        return {"success": True, "articles": articles, "error": None}

    except requests.exceptions.RequestException as e:
        return {
            "success": False, "articles": [],
            "error": f"Failed to connect to NewsAPI: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False, "articles": [],
            "error": f"Unexpected error while fetching news: {str(e)}"
        }


if __name__ == "__main__":
    test_company = "Google"
    print(f"Testing news fetch for {test_company}...")
    result = fetch_company_news(test_company)
    print("Success:", result["success"])
    print("Error:", result["error"])
    print("Articles count:", len(result["articles"]))
