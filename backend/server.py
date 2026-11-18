"""
server.py - FastAPI Enterprise Backend Server
=============================================
Unites all modular routers, provides CORS middleware, starts the APScheduler
monitoring worker, and initializes SQLite tables on startup.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database.db import init_db
from services.monitoring_service import start_monitoring_scheduler

# Import modular routers
from routers.analysis import router as analysis_router
from routers.comparison import router as comparison_router
from routers.intelligence import router as intelligence_router
from routers.search import router as search_router
from routers.trends import router as trends_router
from routers.monitoring import router as monitoring_router
from routers.news import router as news_router
from routers.dashboard import router as dashboard_router
from routers.settings import router as settings_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    init_db()
    start_monitoring_scheduler()
    yield
    # Shutdown actions

app = FastAPI(
    title="AI Competitive Intelligence & Market Strategy Platform",
    description="Enterprise-grade competitive intelligence engine with local NLP, Ollama LLM, RAG semantic search, and multi-competitor comparison.",
    version="3.0.0",
    lifespan=lifespan
)

# Robust CORS configuration for development and local network demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all modular routers
app.include_router(dashboard_router)
app.include_router(analysis_router)
app.include_router(comparison_router)
app.include_router(intelligence_router)
app.include_router(search_router)
app.include_router(trends_router)
app.include_router(monitoring_router)
app.include_router(news_router)
app.include_router(settings_router)

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "3.0.0", "engine": "AI Competitive Intelligence Analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
