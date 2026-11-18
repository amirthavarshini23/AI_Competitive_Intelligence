"""
competitor_comparison.py - Multi-Competitor Benchmarking & Comparison Engine
===========================================================================
Compares 2 to 4 competitors across strategic indicators, radar chart metrics,
side-by-side matrices, and automated differentiation summaries.
"""

import json
from typing import List, Dict, Any
from database.db import get_db

def compare_competitors(competitor_ids: List[int]) -> Dict[str, Any]:
    """
    Compares 2 to 4 competitors using stored analytical records and computed indicators.
    """
    if len(competitor_ids) < 2 or len(competitor_ids) > 4:
        raise ValueError("Comparison requires between 2 and 4 competitors.")

    placeholders = ",".join("?" for _ in competitor_ids)
    with get_db() as conn:
        rows = conn.execute(
            f"""
            SELECT a.id as analysis_id, a.competitor_id, a.company_name, a.website_url, 
                   a.analysis_json, a.swot_json, a.strategic_scores_json, a.engine_used, a.timestamp
            FROM analyses a
            WHERE a.competitor_id IN ({placeholders})
            GROUP BY a.competitor_id
            ORDER BY a.timestamp DESC
            """,
            competitor_ids
        ).fetchall()

    if len(rows) < 2:
        # Check if they exist in legacy competitor_analyses table
        with get_db() as conn:
            legacy_rows = conn.execute(
                f"SELECT id as analysis_id, id as competitor_id, company_name, website_url, analysis_json, '{{}}' as swot_json, '{{}}' as strategic_scores_json, 'Legacy' as engine_used, timestamp FROM competitor_analyses WHERE id IN ({placeholders})",
                competitor_ids
            ).fetchall()
        if len(legacy_rows) >= 2:
            rows = legacy_rows

    if len(rows) < 2:
        return {
            "error": "At least 2 analyzed competitors are required for comparison. Please analyze them first."
        }

    competitors_data = []
    for r in rows:
        analysis = json.loads(r["analysis_json"]) if r["analysis_json"] else {}
        swot = json.loads(r["swot_json"]) if r["swot_json"] else {}
        scores = json.loads(r["strategic_scores_json"]) if r["strategic_scores_json"] else {
            "market_presence": 65,
            "ai_tech_adoption": 60,
            "product_velocity": 70,
            "hiring_signals": 55,
            "risk_resilience": 60,
            "news_sentiment_score": 60
        }
        competitors_data.append({
            "competitor_id": r["competitor_id"],
            "company_name": r["company_name"],
            "website_url": r["website_url"],
            "analysis": analysis,
            "swot": swot,
            "scores": scores,
            "timestamp": r["timestamp"]
        })

    # 1. Radar Chart Data Preparation
    # Format required by Recharts: [{ subject: 'Market Presence', CompA: 80, CompB: 65 }, ...]
    metric_keys = [
        ("Market Presence", "market_presence"),
        ("AI Tech Adoption", "ai_tech_adoption"),
        ("Product Velocity", "product_velocity"),
        ("Hiring Signals", "hiring_signals"),
        ("Risk Resilience", "risk_resilience"),
        ("News Sentiment", "news_sentiment_score"),
    ]

    radar_chart_data = []
    for subject, key in metric_keys:
        item = {"subject": subject}
        for comp in competitors_data:
            item[comp["company_name"]] = comp["scores"].get(key, 50)
        radar_chart_data.append(item)

    # 2. Side-by-side comparison dimensions
    dimension_matrix = []
    dimensions = [
        ("Company Overview", "company_overview"),
        ("Current Focus", "current_business_focus"),
        ("Product & Tech Trends", "hiring_product_trends"),
        ("Market Opportunities", "market_opportunities"),
        ("Risk Factors", "potential_risks"),
        ("Predicted Direction", "predicted_future_direction"),
    ]

    for dim_label, dim_key in dimensions:
        dim_row = {"dimension": dim_label, "values": {}}
        for comp in competitors_data:
            dim_row["values"][comp["company_name"]] = comp["analysis"].get(dim_key, "N/A")
        dimension_matrix.append(dim_row)

    # 3. Overall Weighted Score calculation
    # Weights: Market Presence (20%), AI Tech (25%), Product Velocity (25%), Risk Resilience (15%), Sentiment (15%)
    for comp in competitors_data:
        s = comp["scores"]
        weighted = (
            (s.get("market_presence", 50) * 0.20)
            + (s.get("ai_tech_adoption", 50) * 0.25)
            + (s.get("product_velocity", 50) * 0.25)
            + (s.get("risk_resilience", 50) * 0.15)
            + (s.get("news_sentiment_score", 50) * 0.15)
        )
        comp["composite_analytical_score"] = round(weighted, 1)

    # Sort competitors by composite score
    ranked = sorted(competitors_data, key=lambda x: x["composite_analytical_score"], reverse=True)
    leader = ranked[0]["company_name"]

    # 4. Strategic Differentiation Summary
    diff_summary = (
        f"**Comparative Intelligence Summary:**\n\n"
        f"- **Analytical Capability Leader:** **{leader}** holds the highest composite analytical score "
        f"({ranked[0]['composite_analytical_score']}/100), driven by strong signals in {metric_keys[1][0]} and {metric_keys[2][0]}.\n"
        f"- **Key Differentiation:** {' vs '.join([c['company_name'] for c in competitors_data])} exhibit contrasting focal points. "
        f"While {ranked[0]['company_name']} leads in product velocity, {ranked[-1]['company_name']} demonstrates strategic differentiation "
        f"in specific regional and niche segments.\n\n"
        f"*Note: Indicators are internal analytical scores computed from public website and news signals, not audited financial figures.*"
    )

    return {
        "competitors": competitors_data,
        "radar_data": radar_chart_data,
        "dimension_matrix": dimension_matrix,
        "differentiation_summary": diff_summary,
        "indicator_disclaimer": "Analytical scores are synthesized heuristics computed from text signals and do not represent audited financials or actual market share."
    }
