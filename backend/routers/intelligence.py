"""
routers/intelligence.py - SWOT Analysis & Market Intelligence Router
====================================================================
"""

from fastapi import APIRouter, HTTPException
import json
from database.db import get_db

router = APIRouter(tags=["Intelligence"])

@router.get("/api/swot/{competitor_id}")
def get_competitor_swot(competitor_id: int):
    """Retrieves the latest structured SWOT analysis for a specific competitor."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT a.id, a.company_name, a.swot_json, a.engine_used, a.timestamp 
               FROM analyses a 
               WHERE a.competitor_id = ? 
               ORDER BY a.timestamp DESC LIMIT 1""",
            (competitor_id,)
        ).fetchone()

    if not row:
        raise HTTPException(404, "No analysis found for this competitor.")

    swot_data = json.loads(row["swot_json"]) if row["swot_json"] else {}
    return {
        "competitor_id": competitor_id,
        "company_name": row["company_name"],
        "swot": swot_data,
        "engine_used": row["engine_used"],
        "timestamp": row["timestamp"]
    }

@router.get("/api/market/overview")
def get_market_intelligence_overview():
    """
    Synthesizes cross-competitor opportunities, risk distribution, and category positioning.
    """
    with get_db() as conn:
        analyses = conn.execute(
            """SELECT a.competitor_id, a.company_name, a.analysis_json, a.strategic_scores_json, a.timestamp 
               FROM analyses a 
               GROUP BY a.competitor_id 
               ORDER BY a.timestamp DESC LIMIT 6"""
        ).fetchall()

    if not analyses:
        return {
            "total_evaluated": 0,
            "opportunities": [],
            "risks": [],
            "positioning": []
        }

    opportunities = []
    risks = []
    positioning = []

    for a in analyses:
        parsed = json.loads(a["analysis_json"]) if a["analysis_json"] else {}
        scores = json.loads(a["strategic_scores_json"]) if a["strategic_scores_json"] else {}

        opp_text = parsed.get("market_opportunities", "")
        risk_text = parsed.get("potential_risks", "")

        opportunities.append({
            "company_name": a["company_name"],
            "summary": opp_text[:280] + "..." if len(opp_text) > 280 else opp_text
        })
        risks.append({
            "company_name": a["company_name"],
            "summary": risk_text[:280] + "..." if len(risk_text) > 280 else risk_text
        })
        positioning.append({
            "company_name": a["company_name"],
            "ai_tech_adoption": scores.get("ai_tech_adoption", 50),
            "product_velocity": scores.get("product_velocity", 50),
            "market_presence": scores.get("market_presence", 50),
            "risk_resilience": scores.get("risk_resilience", 50),
        })

    return {
        "total_evaluated": len(analyses),
        "opportunities": opportunities,
        "risks": risks,
        "positioning": positioning
    }
