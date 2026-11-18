"""Legacy analysis bridge"""
from services.intelligence_engine import generate_strategic_intelligence

def analyze_competitor(company_name: str, website_content: str, news_articles: list, api_key: str = None) -> dict:
    res = generate_strategic_intelligence(company_name, website_content, news_articles, use_ollama=True, gemini_key=api_key)
    return {
        "success": True,
        "analysis": res["analysis"],
        "swot": res.get("swot", {}),
        "scores": res.get("strategic_scores", {}),
        "error": None
    }
