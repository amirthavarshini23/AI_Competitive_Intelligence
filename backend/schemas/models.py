"""
models.py - Pydantic Request & Response Data Contracts
======================================================
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalyzeRequest(BaseModel):
    company_name: str = Field(..., description="Name of the competitor")
    website_url: str = Field(..., description="Target website URL")
    gemini_key: Optional[str] = Field(default="", description="Optional Google Gemini API key")
    news_key: Optional[str] = Field(default="", description="Optional NewsAPI key")
    use_ollama: Optional[bool] = Field(default=True, description="Whether to attempt local Ollama LLM")
    ollama_model: Optional[str] = Field(default="qwen2.5:3b", description="Configured Ollama model name")

class SixPillarAnalysis(BaseModel):
    company_overview: str
    current_business_focus: str
    hiring_product_trends: str
    market_opportunities: str
    potential_risks: str
    predicted_future_direction: str

class SWOTQuadrant(BaseModel):
    points: List[str]
    evidence: List[str]
    confidence: str = "Medium"

class SWOTAnalysis(BaseModel):
    strengths: SWOTQuadrant
    weaknesses: SWOTQuadrant
    opportunities: SWOTQuadrant
    threats: SWOTQuadrant

class StrategicScores(BaseModel):
    market_presence: int = Field(default=50, ge=0, le=100)
    ai_tech_adoption: int = Field(default=50, ge=0, le=100)
    product_velocity: int = Field(default=50, ge=0, le=100)
    hiring_signals: int = Field(default=50, ge=0, le=100)
    risk_resilience: int = Field(default=50, ge=0, le=100)
    news_sentiment_score: int = Field(default=50, ge=0, le=100)

class NewsArticleItem(BaseModel):
    title: str
    source: str
    published_date: str
    url: str
    description: str
    content: Optional[str] = ""
    sentiment: Optional[str] = "neutral"
    sentiment_score: Optional[float] = 0.0
    topics: Optional[List[str]] = []

class CompareRequest(BaseModel):
    competitor_ids: List[int] = Field(..., min_length=2, max_length=4)

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    competitor_id: Optional[int] = None
    top_k: Optional[int] = 5

class MonitoringAddRequest(BaseModel):
    competitor_id: int
    check_interval_minutes: Optional[int] = 60

class SystemStatusResponse(BaseModel):
    ollama_available: bool
    ollama_models: List[str]
    selected_model: str
    database_status: str
    total_competitors: int
    total_analyses: int
    total_news_articles: int
    active_monitoring_jobs: int
    embedding_engine: str
