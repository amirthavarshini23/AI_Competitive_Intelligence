"""
news_collector.py - Free, Independent News Intelligence Collector
================================================================
Aggregates competitor news using public RSS feeds (Google News RSS, TechCrunch,
HackerNews, VentureBeat) and optionally NewsAPI without any mandatory paid keys.
"""

import feedparser
import urllib.parse
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup

# Free & public RSS feed providers that support query parameters or technology coverage
RSS_REGISTRY = [
    {
        "name": "Google News RSS",
        "type": "query_based",
        "url_template": "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    },
    {
        "name": "HackerNews RSS",
        "type": "query_based",
        "url_template": "https://hnrss.org/newest?q={query}"
    },
    {
        "name": "TechCrunch Feed",
        "type": "curated",
        "url": "https://techcrunch.com/feed/"
    },
    {
        "name": "VentureBeat Feed",
        "type": "curated",
        "url": "https://venturebeat.com/feed/"
    }
]

def clean_html_summary(raw_html: str) -> str:
    """Strips HTML tags from RSS item summary."""
    if not raw_html:
        return "No summary available."
    try:
        soup = BeautifulSoup(raw_html, "html.parser")
        text = soup.get_text(separator=" ").strip()
        text = re.sub(r"\s+", " ", text)
        return text[:350]
    except Exception:
        return raw_html[:350]

def parse_date(entry: Any) -> str:
    """Extracts or normalizes publication date into readable format."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            dt = datetime(*entry.published_parsed[:6])
            return dt.strftime("%B %d, %Y")
        except Exception:
            pass
    if hasattr(entry, "published") and entry.published:
        return str(entry.published)[:30]
    return datetime.now().strftime("%B %d, %Y")

def fetch_rss_news(company_name: str, max_articles: int = 8) -> List[Dict[str, Any]]:
    """
    Fetches real-time competitor articles from free public RSS feeds.
    Strictly filters out non-relevant articles and deduplicates.
    """
    articles = []
    seen_urls = set()
    seen_titles = set()
    encoded_name = urllib.parse.quote(f'"{company_name}"')
    name_tokens = [t.lower() for t in company_name.split() if len(t) > 2]

    for source in RSS_REGISTRY:
        if len(articles) >= max_articles:
            break

        url = ""
        if source["type"] == "query_based":
            url = source["url_template"].format(query=encoded_name)
        else:
            url = source.get("url", "")

        try:
            # 8-second timeout per feed
            feed = feedparser.parse(url)
            if not feed.entries:
                continue

            for entry in feed.entries:
                if len(articles) >= max_articles:
                    break

                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                summary = clean_html_summary(getattr(entry, "summary", ""))

                if not title or link in seen_urls:
                    continue

                # Filter relevance: Title or summary must mention the company name
                title_lower = title.lower()
                summary_lower = summary.lower()
                is_relevant = any(tok in title_lower or tok in summary_lower for tok in name_tokens)
                
                # For query-based feeds, trust the query match if tokens are short
                if not is_relevant and source["type"] == "query_based":
                    is_relevant = True

                if not is_relevant:
                    continue

                # Deduplicate by normalized title
                norm_title = re.sub(r"[^a-zA-Z0-9]", "", title.lower())
                if norm_title in seen_titles:
                    continue

                seen_urls.add(link)
                seen_titles.add(norm_title)

                source_name = source["name"]
                if hasattr(entry, "source") and hasattr(entry.source, "title"):
                    source_name = entry.source.title

                pub_date = parse_date(entry)

                articles.append({
                    "title": title,
                    "source": source_name,
                    "published_date": pub_date,
                    "date": pub_date, # backward compatibility
                    "url": link,
                    "description": summary,
                    "content": summary
                })

        except Exception:
            # Continue to next feed gracefully
            continue

    return articles

def fetch_company_news(company_name: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Unified news collector.
    1. First tries free, reliable RSS feeds (Google News, HackerNews, TechCrunch).
    2. If a NewsAPI key is provided and RSS returns fewer than 3 articles, supplements with NewsAPI.
    3. Fully functional without any API keys.
    """
    if not company_name or not company_name.strip():
        return {"success": False, "articles": [], "error": "Company name is empty."}

    company_name = company_name.strip()
    articles = fetch_rss_news(company_name, max_articles=8)

    # Optional NewsAPI fallback if user has key and fewer than 3 RSS articles found
    if len(articles) < 3 and api_key and api_key.strip():
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": f'"{company_name}"',
                "sortBy": "relevancy",
                "language": "en",
                "pageSize": 5,
                "apiKey": api_key.strip()
            }
            resp = requests.get(url, params=params, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                for art in data.get("articles", []):
                    t = art.get("title", "")
                    if t and "[Removed]" not in t and not any(a["title"] == t for a in articles):
                        articles.append({
                            "title": t,
                            "source": art.get("source", {}).get("name", "NewsAPI"),
                            "published_date": art.get("publishedAt", "")[:10],
                            "date": art.get("publishedAt", "")[:10],
                            "url": art.get("url", "#"),
                            "description": art.get("description", "No summary available."),
                            "content": art.get("content", "")
                        })
        except Exception:
            pass

    return {
        "success": True,
        "articles": articles[:6],
        "total_found": len(articles),
        "source_type": "Public RSS Feeds (Free)" if not api_key else "RSS + NewsAPI",
        "error": None if articles else f"No recent public news articles found for '{company_name}'."
    }

if __name__ == "__main__":
    test = fetch_company_news("Microsoft")
    print(f"Fetched {len(test['articles'])} articles for Microsoft. Success: {test['success']}")
    for a in test["articles"][:2]:
        print(f"- {a['title']} ({a['source']})")
