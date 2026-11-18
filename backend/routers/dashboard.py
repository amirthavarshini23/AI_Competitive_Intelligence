"""
routers/dashboard.py - Dashboard Summary Metrics & System Status Router
=======================================================================
"""

from fastapi import APIRouter
from database.db import get_db
from services.ollama_service import check_ollama_status

router = APIRouter(tags=["Dashboard"])

@router.get("/api/dashboard/stats")
def get_dashboard_summary():
    """Aggregates high-level metrics for the executive dashboard."""
    with get_db() as conn:
        total_comps = conn.execute("SELECT COUNT(*) FROM competitors").fetchone()[0]
        total_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        
        # If analyses table is 0, check legacy table
        if total_analyses == 0:
            total_analyses = conn.execute("SELECT COUNT(*) FROM competitor_analyses").fetchone()[0]

        total_news = conn.execute("SELECT COUNT(*) FROM news_articles").fetchone()[0]
        active_mon = conn.execute("SELECT COUNT(*) FROM monitoring_jobs WHERE is_active = 1").fetchone()[0]

        recent_analyses = conn.execute(
            """SELECT a.id, a.company_name, a.website_url, a.engine_used, a.timestamp 
               FROM analyses a 
               ORDER BY a.timestamp DESC LIMIT 5"""
        ).fetchall()

        if not recent_analyses:
            recent_analyses = conn.execute("SELECT id, company_name, website_url, 'Extractive NLP' as engine_used, timestamp FROM competitor_analyses ORDER BY timestamp DESC LIMIT 5").fetchall()

        recent_changes = conn.execute(
            """SELECT id, company_name, change_type, change_summary, detected_at 
               FROM detected_changes 
               ORDER BY detected_at DESC LIMIT 4"""
        ).fetchall()

        # Competitor score distribution for quick chart
        scores_dist = conn.execute(
            """SELECT a.company_name, a.strategic_scores_json 
               FROM analyses a 
               GROUP BY a.company_name 
               ORDER BY a.timestamp DESC LIMIT 6"""
        ).fetchall()

    chart_data = []
    for s in scores_dist:
        import json
        sc = json.loads(s["strategic_scores_json"]) if s["strategic_scores_json"] else {}
        chart_data.append({
            "name": s["company_name"],
            "ai_tech": sc.get("ai_tech_adoption", 50),
            "velocity": sc.get("product_velocity", 50),
            "presence": sc.get("market_presence", 50)
        })

    return {
        "total_competitors": total_comps,
        "total_analyses": total_analyses,
        "total_news_articles": total_news,
        "active_monitoring_jobs": active_mon,
        "recent_analyses": [dict(r) for r in recent_analyses],
        "recent_changes": [dict(c) for c in recent_changes],
        "competitor_activity_chart": chart_data
    }

@router.get("/api/stats")
def get_stats_legacy():
    # Backward compatibility
    res = get_dashboard_summary()
    return {
        "total_analyses": res["total_analyses"],
        "recent": res["recent_analyses"]
    }

@router.get("/api/system/status")
def get_system_health():
    """Reports health of Ollama, SQLite, and analytical engines."""
    ollama_info = check_ollama_status()
    with get_db() as conn:
        db_ok = True
        try:
            conn.execute("SELECT 1").fetchone()
        except Exception:
            db_ok = False

    return {
        "status": "online",
        "database_connected": db_ok,
        "ollama_running": ollama_info["running"],
        "ollama_models": ollama_info.get("models", []),
        "default_model": ollama_info.get("default_model", "qwen2.5:3b"),
        "embedding_engine": "L2-Normalized TF-IDF Dense Vectorizer (Local)",
        "nlp_sentiment_engine": "NLTK VADER Lexicon Analyzer",
        "news_collector_engine": "Multi-Source Public RSS Syndication (Google News, TechCrunch, HackerNews)"
    }
