"""
routers/trends.py - Trend Detection & Longitudinal Tracking Router
==================================================================
"""

from fastapi import APIRouter, HTTPException
from database.db import get_db
from services.trend_detector import get_competitor_trend_history

router = APIRouter(tags=["Trends"])

@router.get("/api/trends/competitors")
def get_trend_competitor_list():
    """Lists competitors with historical snapshot counts."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.id, c.name, c.website_url, COUNT(a.id) as snapshot_count, MAX(a.timestamp) as last_updated
               FROM competitors c
               JOIN analyses a ON a.competitor_id = c.id
               GROUP BY c.id
               ORDER BY snapshot_count DESC, c.name ASC"""
        ).fetchall()
    return [dict(r) for r in rows]

@router.get("/api/trends/{competitor_id}")
def get_trends_for_competitor(competitor_id: int):
    """Retrieves chronological shift metrics, timeline, and topic transitions."""
    res = get_competitor_trend_history(competitor_id)
    if "error" in res:
        raise HTTPException(404, res["error"])
    return res
