"""
routers/settings.py - System Configuration & Environment Settings Router
========================================================================
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from services.ollama_service import check_ollama_status

router = APIRouter(tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    default_ollama_model: Optional[str] = "qwen2.5:3b"
    monitoring_interval_minutes: Optional[int] = 60
    enable_rss_news: Optional[bool] = True

_CONFIG = {
    "default_ollama_model": "qwen2.5:3b",
    "monitoring_interval_minutes": 60,
    "enable_rss_news": True,
}

@router.get("/api/settings")
def get_system_settings():
    """Returns runtime configuration and model options."""
    ollama_info = check_ollama_status()
    return {
        "config": _CONFIG,
        "ollama_status": ollama_info,
        "rss_sources": [
            "Google News RSS (Query-Based)",
            "HackerNews RSS (Technology Pulse)",
            "TechCrunch Official RSS",
            "VentureBeat AI/Enterprise RSS"
        ]
    }

@router.post("/api/settings")
def update_system_settings(req: SettingsUpdateRequest):
    """Updates runtime defaults."""
    if req.default_ollama_model:
        _CONFIG["default_ollama_model"] = req.default_ollama_model
    if req.monitoring_interval_minutes:
        _CONFIG["monitoring_interval_minutes"] = req.monitoring_interval_minutes
    if req.enable_rss_news is not None:
        _CONFIG["enable_rss_news"] = req.enable_rss_news
    return {"success": True, "updated_config": _CONFIG}
