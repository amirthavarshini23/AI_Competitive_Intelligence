# AI-Powered Competitive Intelligence & Market Strategy Analyzer

An enterprise-grade, privacy-first competitive intelligence platform that automatically collects public competitor web data, aggregates live news via independent RSS syndication, processes signals using local NLP & machine learning, performs SWOT benchmarking, runs RAG semantic knowledge search, tracks longitudinal market trends, monitors web surface changes, and compiles corporate PDF dossiers.

Designed for college project presentations, technical demonstrations, and AI/ML portfolio resumes. Works **100% free without mandatory paid Gemini API or NewsAPI keys**.

---

## 1. Architectural Overview

```
                                  +-------------------------------------------+
                                  |           React 18 Frontend               |
                                  |  Vite + Tailwind CSS (Light Theme SaaS)   |
                                  +---------------------+---------------------+
                                                        |  HTTP /api/*
                                                        v
                                  +-------------------------------------------+
                                  |          FastAPI Backend Server           |
                                  |        (Uvicorn Daemon :8000)             |
                                  +----+--------------------+---------------+
                                       |                    |               |
               +-----------------------+                    |               +-----------------------+
               v                                            v                                       v
    +--------------------+                       +--------------------+                  +--------------------+
    | Website Scraper    |                       | Free RSS News      |                  | Local NLP & Vector |
    | BeautifulSoup4     |                       | Google News, HN,   |                  | NLTK VADER, TF-IDF |
    | Multi-page Crawl   |                       | TechCrunch, VB     |                  | Cosine Similarity  |
    +--------------------+                       +--------------------+                  +--------------------+
               |                                            |                                       |
               +--------------------------------------------+---------------------------------------+
                                                            |
                                                            v
                                         +--------------------------------------+
                                         |    Dual-Mode Intelligence Engine     |
                                         |  Mode A: Local Ollama (qwen2.5:3b)   |
                                         |  Mode B: Extractive NLP & Rules      |
                                         +------------------+-------------------+
                                                            |
                                   +------------------------+-----------------------+
                                   v                                                v
                    +------------------------------+                 +------------------------------+
                    | SQLite Persistence & Cache   |                 | Corporate ReportLab PDF      |
                    | 10 Tables, Indexes, Hashes   |                 | Multi-Page Numbered Dossier  |
                    +------------------------------+                 +------------------------------+
```

---

## 2. Technology Stack

- **Frontend:** React 18, Vite 5, Tailwind CSS v3, React Router v6, Lucide React, Recharts (Radar, Bar, Line, Scatter), React Markdown, Axios.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic v2.
- **Web Scraping:** BeautifulSoup4, Requests (domain-scoped crawl, SSRF-safe validation, noise cleansing).
- **News Intelligence:** Free RSS syndication via Feedparser (Google News RSS, TechCrunch, HackerNews, VentureBeat).
- **AI/ML Engine:**
  - **Local LLM:** Ollama integration (`qwen2.5:3b`, `llama3.2:3b`, `mistral`).
  - **Deterministic NLP:** Scikit-learn TF-IDF vectorization, NLTK VADER sentiment analysis, cosine similarity, regex entity detection.
  - **Semantic RAG:** Text chunking with overlap, L2-normalized vector embeddings, top-k retrieval, evidence citations (`[1]`, `[2]`).
- **Database:** SQLite3 with 10 tables, foreign key constraints, and indexing.
- **PDF Compilation:** ReportLab (two-pass `NumberedCanvas` with dynamic "Page X of Y" pagination, corporate typography, SWOT tables).
- **Background Worker:** APScheduler for automated competitor change detection.

---

## 3. Key Features

1. **Zero Paid API Requirement:** Works entirely offline and with free public web sources.
2. **Multi-Page Web Intelligence:** Crawls competitor homepage and informative subpages (`/about`, `/products`, `/solutions`).
3. **Independent News Syndication:** Aggregates articles with sentiment classification without requiring NewsAPI.
4. **Six-Pillar Strategic Intelligence:**
   - Company Overview
   - Current Business Focus
   - Hiring & Product Trends
   - Market Opportunities
   - Potential Risks
   - Predicted Future Direction (12–24 months)
5. **Automated SWOT Analysis:** Four-quadrant matrix (Strengths, Weaknesses, Opportunities, Threats) with supporting evidence.
6. **Competitor Benchmarking (2–4 Companies):** Multi-axial radar chart, composite analytical scores, dimension matrices, and differentiation summaries.
7. **RAG-Based Semantic Knowledge Search:** Vector search over indexed passages with grounded answers and citation references.
8. **Longitudinal Trend Detection:** Tracks TF-IDF drift, topic emergence, and keyword decay across historical snapshots.
9. **Website Change Monitoring:** Background change detector using cryptographic SHA-256 content hashes and keyword delta detection.
10. **Corporate PDF Dossier:** Multi-page executive report with cover banner, metadata block, executive summary, 6 pillars, SWOT matrix, and news digest.

---

## 4. Setup & Running Instructions

### Quick Start (Windows)
Double-click **`START_PROJECT.bat`** in the project root. It will automatically start both the backend and frontend in separate terminal windows.

---

### Manual Step-by-Step Start

#### 1. Backend Startup
```powershell
cd "D:\Agentic AI\AI_Competitive_Intelligence\backend"
python server.py
```
* Backend API: **http://localhost:8000**
* Interactive Swagger Docs: **http://localhost:8000/docs**

#### 2. Frontend Startup
```powershell
cd "D:\Agentic AI\AI_Competitive_Intelligence\frontend"
npm run dev
```
* React Web Dashboard: **http://localhost:5173**

---

## 5. Local Ollama LLM Setup (Optional but Recommended)

The application includes an automatic fallback: if Ollama is not running, it seamlessly operates using its built-in **Extractive NLP and Rule-Based engine**.

To enable local neural generation:
1. Ensure Ollama is installed (download from [ollama.com](https://ollama.com)).
2. Pull the recommended lightweight model:
   ```powershell
   ollama run qwen2.5:3b
   ```
3. Keep Ollama running in the background. The platform will automatically detect it at `http://localhost:11434`.

---

## 6. Live Presentation Demonstration Script

Follow these steps for a live presentation or grading demonstration:

- **Step 1: Dashboard Overview (`/`)**
  Show total competitors analyzed, reports generated, and the strategic indicator bar chart.
- **Step 2: Run New Analysis (`/analyze`)**
  - Name: `Microsoft`
  - URL: `https://www.microsoft.com`
  - Click **Start Competitive Analysis**.
  - Show the 4 animated progress stages (Scraping -> News -> NLP/AI -> Dossier).
- **Step 3: Strategic Dossier (`/report/:id`)**
  - Review the 6 strategic dimensions in the organized tabs.
  - Switch to the **SWOT Analysis** tab to showcase the 4-quadrant strategic matrix.
  - Switch to the **News Coverage** tab to show VADER sentiment tags and RSS sources.
- **Step 4: Competitor Comparison (`/compare`)**
  - Select `Microsoft` and another competitor (e.g. `Anthropic` or `OpenAI`).
  - Demonstrate the **Strategic Radar Chart**, the composite score bar chart, and the differentiation summary.
- **Step 5: RAG Semantic Search (`/search`)**
  - Ask: *"What are Microsoft's primary cloud and AI solutions?"*
  - Show the synthesized answer with citation markers `[1]`, `[2]` and the underlying retrieved text chunks.
- **Step 6: Longitudinal Trend Analysis (`/trends`)**
  - Select a competitor with multiple snapshots.
  - Review the shift score percentage, emerging vs. declining keywords, and TF-IDF evolution.
- **Step 7: Competitor Monitoring (`/monitoring`)**
  - Show monitored surfaces and click **Check Now** to run an immediate SHA-256 fingerprint check.
- **Step 8: Download PDF Report**
  - Click **Download Corporate PDF Report** to produce the multi-page ReportLab document.

---

## 7. Verification & Automated Test Suite

Run the full 10-point test suite:
```powershell
python backend/tests/test_pipeline.py
```

### Verified Test Results:
- [x] URL validation and SSRF safety
- [x] Local NLP, TF-IDF, and VADER sentiment analysis
- [x] SQLite database schema and foreign key constraints
- [x] RAG text chunking, vector indexing, and cosine similarity
- [x] 6-Pillar strategic intelligence & SWOT synthesis
- [x] Competitor comparison radar metrics and scoring
- [x] SHA-256 fingerprint change monitoring
- [x] ReportLab corporate PDF dossier compilation
- [x] Public RSS news syndication parsing
- [x] Temporary test record cleanup

---

## 8. Network Dependencies & Limitations

- **Features requiring internet access:**
  - Scraping live competitor websites (requires accessible public target URL).
  - Fetching real-time RSS feeds (Google News, TechCrunch).
- **Features working 100% offline:**
  - Local NLP processing, TF-IDF vectorization, keyword extraction.
  - VADER sentiment analysis.
  - Local Ollama LLM inference.
  - RAG vector indexing and semantic retrieval.
  - Competitor comparison and radar metrics.
  - Historical trend tracking.
  - ReportLab corporate PDF dossier generation.
  - SQLite data persistence.
