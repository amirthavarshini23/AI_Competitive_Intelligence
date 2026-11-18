"""
monitoring_service.py - Competitor Website Change Detection & Background Monitor
================================================================================
Monitors competitor web surfaces on a scheduled cadence using APScheduler.
Computes cryptographic content hashes, extracts new keywords, and logs diff alerts.
"""

import hashlib
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler

from database.db import get_db
from services.scraper import extract_single_page, clean_url
from services.nlp_engine import extract_top_keywords

logger = logging.getLogger("MonitoringService")

# Global background scheduler
scheduler = BackgroundScheduler(daemon=True)
_is_scheduler_running = False

def start_monitoring_scheduler():
    """Initializes and starts the APScheduler background thread."""
    global _is_scheduler_running
    if not _is_scheduler_running:
        try:
            scheduler.start()
            _is_scheduler_running = True
            logger.info("Monitoring APScheduler started successfully.")
        except Exception as e:
            logger.error(f"Failed to start APScheduler: {e}")

def hash_content(text: str) -> str:
    """Computes SHA-256 fingerprint of sanitized content."""
    return hashlib.sha256((text or "").strip().encode("utf-8")).hexdigest()

def check_competitor_changes(competitor_id: int) -> Dict[str, Any]:
    """
    Executes a change-detection check for a specific competitor.
    Fetches the website, compares with latest snapshot, and records detected changes.
    """
    with get_db() as conn:
        job = conn.execute(
            "SELECT * FROM monitoring_jobs WHERE competitor_id = ?", (competitor_id,)
        ).fetchone()
        if not job:
            return {"error": "Monitoring job not found for this competitor."}

        company_name = job["company_name"]
        website_url = job["website_url"]

        # Fetch latest stored snapshot
        prev_snapshot = conn.execute(
            """SELECT * FROM competitor_snapshots 
               WHERE competitor_id = ? 
               ORDER BY timestamp DESC LIMIT 1""",
            (competitor_id,)
        ).fetchone()

    # Re-scrape website
    page_res = extract_single_page(clean_url(website_url))
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    next_check_str = (datetime.now() + timedelta(minutes=job["check_interval_minutes"])).strftime("%Y-%m-%d %H:%M:%S")

    if page_res.get("error"):
        with get_db() as conn:
            conn.execute(
                "UPDATE monitoring_jobs SET last_checked = ?, status = 'error' WHERE competitor_id = ?",
                (now_str, competitor_id)
            )
        return {"has_changed": False, "status": "fetch_error", "error": page_res["error"]}

    current_content = page_res.get("content", "")
    current_hash = hash_content(current_content)
    current_keywords = [k["term"] for k in extract_top_keywords(current_content, top_n=12)]

    has_changed = False
    change_summary = "No significant changes detected."
    new_keywords = []

    if prev_snapshot:
        prev_hash = prev_snapshot["content_hash"]
        prev_keywords = json.loads(prev_snapshot["keywords_json"]) if prev_snapshot["keywords_json"] else []

        if current_hash != prev_hash:
            has_changed = True
            new_keywords = [kw for kw in current_keywords if kw not in prev_keywords]
            
            # Detect whether headings or content changed
            summary_parts = ["Website text modified."]
            if new_keywords:
                summary_parts.append(f"New terms detected: {', '.join(new_keywords[:4])}.")
            
            # Detect product announcements
            if any(term in current_content.lower() for term in ["launch", "announcing", "new version", "introducing"]):
                summary_parts.append("Product announcement signals identified.")

            change_summary = " ".join(summary_parts)

            # Record detected change in database
            with get_db() as conn:
                conn.execute(
                    """INSERT INTO detected_changes 
                       (competitor_id, company_name, change_type, change_summary, new_keywords_json, detected_at, viewed)
                       VALUES (?, ?, ?, ?, ?, ?, 0)""",
                    (competitor_id, company_name, "Content Update", change_summary, json.dumps(new_keywords), now_str)
                )
    else:
        # First snapshot baseline
        change_summary = "Initial monitoring baseline created."

    # Save new snapshot & update job status
    with get_db() as conn:
        conn.execute(
            """INSERT INTO competitor_snapshots 
               (competitor_id, website_url, content_hash, text_sample, keywords_json, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (competitor_id, website_url, current_hash, current_content[:3000], json.dumps(current_keywords), now_str)
        )
        conn.execute(
            """UPDATE monitoring_jobs 
               SET last_checked = ?, next_check = ?, status = 'healthy' 
               WHERE competitor_id = ?""",
            (now_str, next_check_str, competitor_id)
        )

    return {
        "has_changed": has_changed,
        "company_name": company_name,
        "last_checked": now_str,
        "next_check": next_check_str,
        "change_summary": change_summary,
        "new_keywords": new_keywords,
        "status": "healthy"
    }

def add_monitoring_job(competitor_id: int, interval_minutes: int = 60) -> Dict[str, Any]:
    """Adds a competitor to the monitoring list and takes an immediate baseline."""
    with get_db() as conn:
        comp = conn.execute("SELECT id, name, website_url FROM competitors WHERE id = ?", (competitor_id,)).fetchone()
        if not comp:
            return {"error": "Competitor not found."}

        next_check = (datetime.now() + timedelta(minutes=interval_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            """INSERT INTO monitoring_jobs 
               (competitor_id, company_name, website_url, check_interval_minutes, next_check, is_active, status)
               VALUES (?, ?, ?, ?, ?, 1, 'active')
               ON CONFLICT(competitor_id) DO UPDATE SET 
               check_interval_minutes = excluded.check_interval_minutes, is_active = 1""",
            (competitor_id, comp["name"], comp["website_url"], interval_minutes, next_check)
        )

    # Run initial baseline check immediately
    res = check_competitor_changes(competitor_id)
    return {"success": True, "job": res}
