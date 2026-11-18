"""
routers/monitoring.py - Competitor Web Surface Change Monitoring Router
======================================================================
"""

from fastapi import APIRouter, HTTPException
from database.db import get_db
from schemas.models import MonitoringAddRequest
from services.monitoring_service import add_monitoring_job, check_competitor_changes

router = APIRouter(tags=["Monitoring"])

@router.get("/api/monitoring")
def list_monitoring_jobs():
    """Lists all monitored competitors and their check status."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT mj.id, mj.competitor_id, mj.company_name, mj.website_url, 
                      mj.check_interval_minutes, mj.last_checked, mj.next_check, 
                      mj.is_active, mj.status,
                      (SELECT COUNT(*) FROM detected_changes dc WHERE dc.competitor_id = mj.competitor_id) as change_count
               FROM monitoring_jobs mj
               ORDER BY mj.last_checked DESC"""
        ).fetchall()
    return [dict(r) for r in rows]

@router.post("/api/monitoring/add")
def add_competitor_to_monitoring(req: MonitoringAddRequest):
    """Adds a competitor to automated change tracking."""
    res = add_monitoring_job(req.competitor_id, req.check_interval_minutes or 60)
    if "error" in res:
        raise HTTPException(400, res["error"])
    return res

@router.post("/api/monitoring/check/{competitor_id}")
def check_competitor_now(competitor_id: int):
    """Triggers an immediate manual check of competitor website for modifications."""
    res = check_competitor_changes(competitor_id)
    if "error" in res:
        raise HTTPException(400, res["error"])
    return res

@router.get("/api/monitoring/changes")
def get_detected_changes(limit: int = 20):
    """Retrieves recent detected content and keyword modification alerts."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, competitor_id, company_name, change_type, change_summary, 
                      new_keywords_json, detected_at, viewed 
               FROM detected_changes 
               ORDER BY detected_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
