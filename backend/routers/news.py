"""
routers/news.py - News Intelligence, Sentiment & Source Filtering Router
========================================================================
"""

from fastapi import APIRouter, Query
from typing import Optional
from database.db import get_db

router = APIRouter(tags=["News"])

@router.get("/api/news")
def get_collected_news(
    competitor_id: Optional[int] = Query(None),
    sentiment: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50)
):
    """Retrieves collected news articles with multi-factor filters and VADER sentiment."""
    query = """
        SELECT na.id, na.competitor_id, c.name as company_name, na.title, na.source, 
               na.published_date, na.url, na.description, na.sentiment, na.sentiment_score, na.timestamp
        FROM news_articles na
        LEFT JOIN competitors c ON c.id = na.competitor_id
        WHERE 1=1
    """
    params = []

    if competitor_id:
        query += " AND na.competitor_id = ?"
        params.append(competitor_id)
    if sentiment:
        query += " AND na.sentiment = ?"
        params.append(sentiment.lower())
    if search and search.strip():
        query += " AND (na.title LIKE ? OR na.description LIKE ?)"
        term = f"%{search.strip()}%"
        params.extend([term, term])

    query += " ORDER BY na.id DESC LIMIT ?"
    params.append(limit)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(r) for r in rows]

@router.get("/api/news/stats")
def get_news_sentiment_stats():
    """Aggregates sentiment distribution and top sources across all collected news."""
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM news_articles").fetchone()[0]
        pos = conn.execute("SELECT COUNT(*) FROM news_articles WHERE sentiment = 'positive'").fetchone()[0]
        neu = conn.execute("SELECT COUNT(*) FROM news_articles WHERE sentiment = 'neutral'").fetchone()[0]
        neg = conn.execute("SELECT COUNT(*) FROM news_articles WHERE sentiment = 'negative'").fetchone()[0]

        sources = conn.execute(
            "SELECT source, COUNT(*) as count FROM news_articles GROUP BY source ORDER BY count DESC LIMIT 8"
        ).fetchall()

    return {
        "total_articles": total,
        "sentiment_distribution": {
            "positive": pos,
            "neutral": neu,
            "negative": neg
        },
        "top_sources": [dict(s) for s in sources],
        "disclaimer": "News sentiment reflects public reporting tone and does not represent audited company performance."
    }
