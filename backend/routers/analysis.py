"""
routers/analysis.py - Main Analysis & Intelligence Pipeline Endpoints
====================================================================
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json
import io
import urllib.parse
from datetime import datetime

from database.db import get_db
from schemas.models import AnalyzeRequest
from services.scraper import scrape_website_multi_page, clean_url
from services.news_collector import fetch_company_news
from services.nlp_engine import analyze_sentiment
from services.intelligence_engine import generate_strategic_intelligence
from services.semantic_search import index_competitor_content
from services.report_generator import generate_pdf_report

router = APIRouter(tags=["Analysis"])

@router.post("/api/analyze")
def run_full_analysis(req: AnalyzeRequest):
    """Executes the complete end-to-end 4-stage competitive analysis pipeline."""
    company_name = req.company_name.strip()
    raw_url = req.website_url.strip()

    if not company_name:
        raise HTTPException(400, "Competitor name cannot be empty.")
    if not raw_url:
        raise HTTPException(400, "Website URL cannot be empty.")

    clean_target_url = clean_url(raw_url)
    domain = urllib.parse.urlparse(clean_target_url).netloc.lower()

    # 1. Register or retrieve Competitor in SQLite
    with get_db() as conn:
        comp_row = conn.execute("SELECT id FROM competitors WHERE name = ?", (company_name,)).fetchone()
        if comp_row:
            competitor_id = comp_row["id"]
            conn.execute(
                "UPDATE competitors SET website_url = ?, domain = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (clean_target_url, domain, competitor_id)
            )
        else:
            cur = conn.execute(
                "INSERT INTO competitors (name, website_url, domain) VALUES (?, ?, ?)",
                (company_name, clean_target_url, domain)
            )
            competitor_id = cur.lastrowid

    # 2. Stage 1: Website Scraping
    scrape_res = scrape_website_multi_page(clean_target_url, max_subpages=2)
    website_text = scrape_res.get("combined_text", "")
    scraped_pages = scrape_res.get("pages", [])

    # Store scraped pages in database
    with get_db() as conn:
        for page in scraped_pages:
            if not page.get("error"):
                conn.execute(
                    """INSERT INTO scraped_documents 
                       (competitor_id, url, title, meta_description, headings_json, content, char_count) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        competitor_id, page.get("url", clean_target_url),
                        page.get("title", ""), page.get("meta_description", ""),
                        json.dumps(page.get("headings", [])), page.get("content", ""),
                        len(page.get("content", ""))
                    )
                )

    # 3. Stage 2: Index Content for RAG & Semantic Search
    index_competitor_content(competitor_id, clean_target_url, website_text)

    # 4. Stage 3: Independent Public News Collection & Sentiment Analysis
    news_res = fetch_company_news(company_name, req.news_key)
    raw_articles = news_res.get("articles", [])
    processed_articles = []

    with get_db() as conn:
        for art in raw_articles:
            # Perform local VADER sentiment analysis
            sent = analyze_sentiment(art["title"] + " " + art.get("description", ""))
            art["sentiment"] = sent["label"]
            art["sentiment_score"] = sent["compound"]
            processed_articles.append(art)

            conn.execute(
                """INSERT INTO news_articles 
                   (competitor_id, title, source, published_date, url, description, content, sentiment, sentiment_score)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    competitor_id, art["title"], art["source"], art["published_date"],
                    art["url"], art["description"], art.get("content", ""),
                    sent["label"], sent["compound"]
                )
            )

    # 5. Stage 4: Strategic Intelligence & SWOT Synthesis
    intelligence_res = generate_strategic_intelligence(
        company_name=company_name,
        website_text=website_text,
        news_articles=processed_articles,
        use_ollama=req.use_ollama,
        ollama_model=req.ollama_model,
        gemini_key=req.gemini_key
    )

    analysis_data = intelligence_res["analysis"]
    swot_data = intelligence_res["swot"]
    scores_data = intelligence_res["strategic_scores"]
    engine_used = intelligence_res["engine_used"]
    model_name = intelligence_res.get("model_name", "local")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 6. Save Analysis to Database
    with get_db() as conn:
        # Save in analyses table
        cur = conn.execute(
            """INSERT INTO analyses 
               (competitor_id, company_name, website_url, analysis_json, swot_json, strategic_scores_json, engine_used, model_name, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                competitor_id, company_name, clean_target_url,
                json.dumps(analysis_data), json.dumps(swot_data), json.dumps(scores_data),
                engine_used, model_name, now_str
            )
        )
        analysis_id = cur.lastrowid

        # Save in analysis_history for tracking
        conn.execute(
            """INSERT INTO analysis_history (competitor_id, analysis_id, metric_snapshots_json, timestamp)
               VALUES (?, ?, ?, ?)""",
            (competitor_id, analysis_id, json.dumps(scores_data), now_str)
        )

        # Legacy table synchronization
        conn.execute(
            """INSERT INTO competitor_analyses (id, company_name, website_url, analysis_json, news_json, scraped_content, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (analysis_id, company_name, clean_target_url, json.dumps(analysis_data), json.dumps(processed_articles), website_text[:3000], now_str)
        )

    return {
        "success": True,
        "analysis_id": analysis_id,
        "competitor_id": competitor_id,
        "company_name": company_name,
        "website_url": clean_target_url,
        "analysis": analysis_data,
        "swot": swot_data,
        "scores": scores_data,
        "news_articles": processed_articles,
        "engine_used": engine_used,
        "scrape_success": scrape_res["success"],
        "news_success": news_res["success"],
        "timestamp": now_str
    }

@router.get("/api/analyses")
def list_all_analyses():
    """Lists all historical strategic analyses."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT a.id, a.competitor_id, a.company_name, a.website_url, a.engine_used, a.timestamp 
               FROM analyses a 
               ORDER BY a.timestamp DESC"""
        ).fetchall()
        
        # Fallback to legacy table if analyses is empty
        if not rows:
            legacy = conn.execute("SELECT id, id as competitor_id, company_name, website_url, 'Extractive' as engine_used, timestamp FROM competitor_analyses ORDER BY timestamp DESC").fetchall()
            return [dict(r) for r in legacy]

    return [dict(r) for r in rows]

# Backward compatibility alias
@router.get("/api/history")
def get_history_legacy():
    return list_all_analyses()

@router.get("/api/analyses/{analysis_id}")
def get_analysis_details(analysis_id: int):
    """Retrieves full details for a single analysis."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()

        if not row:
            # Check legacy table
            leg = conn.execute("SELECT * FROM competitor_analyses WHERE id = ?", (analysis_id,)).fetchone()
            if not leg:
                raise HTTPException(404, "Analysis not found.")
            data = dict(leg)
            data["analysis"] = json.loads(data["analysis_json"])
            data["news"] = json.loads(data["news_json"])
            data["swot"] = {}
            data["scores"] = {}
            data["engine_used"] = "Extractive NLP"
            return data

        data = dict(row)
        data["analysis"] = json.loads(data["analysis_json"])
        data["swot"] = json.loads(data["swot_json"]) if data["swot_json"] else {}
        data["scores"] = json.loads(data["strategic_scores_json"]) if data["strategic_scores_json"] else {}
        
        # Load related news articles
        news_rows = conn.execute(
            "SELECT title, source, published_date, url, description, sentiment, sentiment_score FROM news_articles WHERE competitor_id = ? ORDER BY id DESC LIMIT 10",
            (data["competitor_id"],)
        ).fetchall()
        data["news"] = [dict(n) for n in news_rows]

    return data

@router.get("/api/analysis/{analysis_id}")
def get_analysis_legacy(analysis_id: int):
    return get_analysis_details(analysis_id)

@router.delete("/api/analyses/{analysis_id}")
def delete_analysis(analysis_id: int):
    """Deletes an analysis record."""
    with get_db() as conn:
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.execute("DELETE FROM competitor_analyses WHERE id = ?", (analysis_id,))
    return {"success": True}

@router.delete("/api/analysis/{analysis_id}")
def delete_analysis_legacy(analysis_id: int):
    return delete_analysis(analysis_id)

@router.get("/api/analyses/{analysis_id}/pdf")
def download_analysis_pdf(analysis_id: int):
    """Generates and downloads the executive ReportLab PDF dossier."""
    data = get_analysis_details(analysis_id)
    pdf_bytes = generate_pdf_report(
        company_name=data["company_name"],
        url=data["website_url"],
        analysis_data=data["analysis"],
        news_articles=data.get("news", []),
        swot_data=data.get("swot", {}),
        engine_used=data.get("engine_used", "Strategic Analysis")
    )
    filename = f"Intelligence_Dossier_{data['company_name'].replace(' ', '_')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/api/report/{analysis_id}/pdf")
def download_pdf_legacy(analysis_id: int):
    return download_analysis_pdf(analysis_id)
