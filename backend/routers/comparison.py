"""
routers/comparison.py - Competitor Comparison & Benchmarking Router
===================================================================
"""

from fastapi import APIRouter, HTTPException
from database.db import get_db
from schemas.models import CompareRequest
from services.competitor_comparison import compare_competitors

router = APIRouter(tags=["Comparison"])

@router.get("/api/compare/competitors")
def get_available_competitors():
    """Returns list of competitors that have been analyzed and can be compared."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT c.id, c.name, c.website_url, COUNT(a.id) as analysis_count, MAX(a.timestamp) as latest_analysis
               FROM competitors c
               JOIN analyses a ON a.competitor_id = c.id
               GROUP BY c.id
               ORDER BY c.name ASC"""
        ).fetchall()
        
        # Fallback to legacy if empty
        if not rows:
            legacy = conn.execute("SELECT id, company_name as name, website_url, 1 as analysis_count, timestamp as latest_analysis FROM competitor_analyses GROUP BY company_name").fetchall()
            return [dict(r) for r in legacy]

    return [dict(r) for r in rows]

@router.post("/api/compare")
def compare_selected_competitors(req: CompareRequest):
    """Generates comparison matrix, radar charts, and differentiation summaries for 2-4 competitors."""
    try:
        res = compare_competitors(req.competitor_ids)
        if "error" in res:
            raise HTTPException(400, res["error"])
        return res
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Comparison error: {str(e)}")
