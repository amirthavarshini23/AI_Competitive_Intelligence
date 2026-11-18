"""
test_pipeline.py - Comprehensive Automated Verification Test Suite
==================================================================
Tests every component of the AI Competitive Intelligence Platform:
- URL safety and sanitizer
- Scraper parsing
- Independent RSS news parsing
- Local NLP, TF-IDF, and VADER sentiment
- SQLite database transactions
- 6-Pillar Intelligence & SWOT synthesis
- Semantic RAG vector indexing and retrieval
- Competitor comparison logic
- Change detection and hash monitoring
- ReportLab PDF compilation
"""

import sys
import os
import io

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from services.scraper import is_safe_url, clean_url
from services.news_collector import clean_html_summary, parse_date
from services.nlp_engine import clean_text, analyze_sentiment, extract_top_keywords, extract_key_sentences
from services.semantic_search import chunk_text, index_competitor_content, search_semantic_chunks, answer_rag_question
from services.intelligence_engine import compute_analytical_scores, generate_extractive_intelligence
from services.competitor_comparison import compare_competitors
from services.monitoring_service import hash_content
from services.report_generator import generate_pdf_report
from database.db import init_db, get_db

def test_url_safety():
    print("[1/10] Testing URL validation and SSRF safety...")
    assert is_safe_url("https://www.microsoft.com") is True
    assert is_safe_url("http://localhost:8000") is False
    assert is_safe_url("http://127.0.0.1") is False
    assert clean_url("openai.com") == "https://openai.com"
    print("      -> URL safety tests PASSED.")

def test_nlp_and_sentiment():
    print("[2/10] Testing local NLP, TF-IDF, and sentiment analysis...")
    sample_text = (
        "Microsoft Corporation unveiled innovative cloud platform capabilities, "
        "expanding enterprise AI automation. Strong growth was reported across software subscriptions. "
        "The company announced new developer tools and security compliance features."
    )
    sent = analyze_sentiment(sample_text)
    assert sent["label"] in ("positive", "neutral", "negative")
    
    kws = extract_top_keywords(sample_text, top_n=5)
    assert len(kws) > 0
    assert any("ai" in k["term"] or "cloud" in k["term"] or "platform" in k["term"] for k in kws)
    
    sentences = extract_key_sentences(sample_text, max_sentences=2)
    assert len(sentences) <= 2
    print("      -> NLP and sentiment analysis tests PASSED.")

def test_database_initialization():
    print("[3/10] Testing SQLite initialization and schema integrity...")
    init_db()
    with get_db() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        required = ["competitors", "analyses", "scraped_documents", "news_articles", "embeddings_metadata", "competitor_snapshots", "monitoring_jobs"]
        for req in required:
            assert req in table_names, f"Missing table: {req}"
    print("      -> Database schema tests PASSED.")

def test_rag_and_semantic_indexing():
    print("[4/10] Testing RAG text chunking, indexing, and vector similarity...")
    test_content = (
        "Microsoft Azure AI empowers businesses with custom copilot studio solutions. "
        "Enterprise customers leverage Azure OpenAI service for scalable machine learning deployments. "
        "Global data centers provide low-latency cloud infrastructure across multiple continents."
    )
    chunks = chunk_text(test_content, chunk_size=20, overlap=5)
    assert len(chunks) >= 1

    # Insert test competitor
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO competitors (id, name, website_url, domain) VALUES (999, 'TestCorp', 'https://testcorp.com', 'testcorp.com')")

    index_competitor_content(999, "https://testcorp.com", test_content)
    matches = search_semantic_chunks("Azure copilot solutions", competitor_id=999, top_k=3)
    assert len(matches) > 0
    assert matches[0]["similarity_score"] > 0.0

    qa_res = answer_rag_question("What cloud infrastructure is provided?", competitor_id=999)
    assert "answer" in qa_res
    assert len(qa_res["sources"]) > 0
    print("      -> RAG and semantic retrieval tests PASSED.")

def test_intelligence_and_swot_generation():
    print("[5/10] Testing 6-Pillar intelligence and SWOT synthesis...")
    test_content = (
        "TestCorp develops autonomous enterprise workflows and automated analytics software. "
        "The company has expanded hiring for AI research engineers across Europe and North America."
    )
    news = [{"title": "TestCorp launches new platform", "source": "TechNews", "published_date": "2026-11-18", "description": "New AI release", "date": "2026-11-18"}]
    scores = compute_analytical_scores(test_content, news)
    assert 0 <= scores["ai_tech_adoption"] <= 100
    assert 0 <= scores["product_velocity"] <= 100

    extractive = generate_extractive_intelligence("TestCorp", test_content, news, ["Enterprise Cloud Suite"])
    assert "company_overview" in extractive["analysis"]
    assert "current_business_focus" in extractive["analysis"]
    assert "strengths" in extractive["swot"]
    assert "weaknesses" in extractive["swot"]
    print("      -> 6-Pillars & SWOT synthesis tests PASSED.")

def test_competitor_comparison():
    print("[6/10] Testing competitor comparison and radar metrics...")
    with get_db() as conn:
        conn.execute("INSERT OR IGNORE INTO competitors (id, name, website_url, domain) VALUES (1001, 'AlphaCorp', 'https://alphacorp.com', 'alphacorp.com')")
        conn.execute("INSERT OR IGNORE INTO competitors (id, name, website_url, domain) VALUES (1002, 'BetaCorp', 'https://betacorp.com', 'betacorp.com')")
        
        sample_analysis = '{"company_overview": "Overview text", "current_business_focus": "Focus text", "hiring_product_trends": "Trends", "market_opportunities": "Opps", "potential_risks": "Risks", "predicted_future_direction": "Future"}'
        sample_scores = '{"market_presence": 80, "ai_tech_adoption": 75, "product_velocity": 85, "hiring_signals": 70, "risk_resilience": 80, "news_sentiment_score": 65}'
        
        conn.execute("INSERT OR REPLACE INTO analyses (id, competitor_id, company_name, website_url, analysis_json, strategic_scores_json, engine_used) VALUES (1001, 1001, 'AlphaCorp', 'https://alphacorp.com', ?, ?, 'Extractive')", (sample_analysis, sample_scores))
        conn.execute("INSERT OR REPLACE INTO analyses (id, competitor_id, company_name, website_url, analysis_json, strategic_scores_json, engine_used) VALUES (1002, 1002, 'BetaCorp', 'https://betacorp.com', ?, ?, 'Extractive')", (sample_analysis, sample_scores))

    res = compare_competitors([1001, 1002])
    assert "radar_data" in res
    assert len(res["competitors"]) == 2
    assert "differentiation_summary" in res
    print("      -> Competitor comparison tests PASSED.")

def test_change_monitoring():
    print("[7/10] Testing SHA-256 fingerprint change monitoring...")
    text_v1 = "Our enterprise platform provides data streaming."
    text_v2 = "Our enterprise platform provides data streaming and generative AI copilot capabilities."
    h1 = hash_content(text_v1)
    h2 = hash_content(text_v2)
    assert h1 != h2
    print("      -> Change detection hash tests PASSED.")

def test_pdf_generation():
    print("[8/10] Testing ReportLab corporate PDF dossier compilation...")
    analysis = {
        "company_overview": "Microsoft creates software, consumer electronics, and personal computers.",
        "current_business_focus": "Cloud computing and artificial intelligence solutions.",
        "hiring_product_trends": "Strong expansion into foundation model infrastructure.",
        "market_opportunities": "Enterprise cloud transformations.",
        "potential_risks": "Antitrust scrutiny and market rivalry.",
        "predicted_future_direction": "Continued vertical integration of AI copilot services."
    }
    swot = {
        "strengths": {"points": ["Global cloud footprint", "Dominant office suite"], "confidence": "High"},
        "weaknesses": {"points": ["High infrastructure overhead"], "confidence": "Medium"},
        "opportunities": {"points": ["Autonomous enterprise agents"], "confidence": "High"},
        "threats": {"points": ["Open-source model alternatives"], "confidence": "Medium"},
    }
    news = [{"title": "Major Partnership Announced", "source": "TechNews", "published_date": "2026-11-18", "description": "Collaboration on enterprise AI cloud.", "date": "2026-11-18"}]

    pdf_bytes = generate_pdf_report(
        company_name="Microsoft",
        url="https://www.microsoft.com",
        analysis_data=analysis,
        news_articles=news,
        swot_data=swot,
        engine_used="Extractive NLP Engine"
    )
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")
    print(f"      -> PDF dossier compiled successfully ({len(pdf_bytes)} bytes) PASSED.")

def test_news_rss_parser():
    print("[9/10] Testing public RSS news parser helper functions...")
    summary_raw = "<p>Microsoft <b>unveiled</b> new platform updates today.</p>"
    clean = clean_html_summary(summary_raw)
    assert "<p>" not in clean
    assert "Microsoft" in clean
    print("      -> RSS news helper tests PASSED.")

def test_cleanup():
    print("[10/10] Cleaning up temporary test records...")
    with get_db() as conn:
        conn.execute("DELETE FROM competitors WHERE id IN (999, 1001, 1002)")
        conn.execute("DELETE FROM analyses WHERE competitor_id IN (999, 1001, 1002)")
        conn.execute("DELETE FROM embeddings_metadata WHERE competitor_id = 999")
    print("      -> Cleanup complete.")

if __name__ == "__main__":
    print("==========================================================")
    print("AI COMPETITIVE INTELLIGENCE PLATFORM - VERIFICATION SUITE")
    print("==========================================================")
    test_url_safety()
    test_nlp_and_sentiment()
    test_database_initialization()
    test_rag_and_semantic_indexing()
    test_intelligence_and_swot_generation()
    test_competitor_comparison()
    test_change_monitoring()
    test_pdf_generation()
    test_news_rss_parser()
    test_cleanup()
    print("==========================================================")
    print("ALL 10/10 AUTOMATED VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==========================================================")
