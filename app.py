"""
app.py - AI Competitive Intelligence Analyzer (Streamlit Dashboard)
====================================================================
Main entry point. Provides:
  - Modern themed UI with custom CSS
  - Sidebar for API keys and analysis history (SQLite)
  - Step-by-step progress spinners (Scraping → News → Gemini → Saving)
  - Tabbed results dashboard with 7 intelligence views
  - One-click PDF download via ReportLab
"""

import streamlit as st
import os
import json
import sqlite3
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Import project modules
from scraper import scrape_website
from news_agent import fetch_company_news
from analysis import analyze_competitor
from report_generator import generate_pdf_report

# ---------------------------------------------------------------------------
# DATABASE LAYER
# ---------------------------------------------------------------------------
DB_PATH = "database/competitors.db"


def init_db():
    """Create the SQLite database and table if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competitor_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            website_url TEXT NOT NULL,
            analysis_json TEXT NOT NULL,
            news_json TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_analysis(name: str, url: str, analysis: dict, news: list):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO competitor_analyses (company_name, website_url, analysis_json, news_json, timestamp) VALUES (?,?,?,?,?)",
        (name, url, json.dumps(analysis), json.dumps(news), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, company_name, website_url, timestamp FROM competitor_analyses ORDER BY timestamp DESC"
    ).fetchall()
    conn.close()
    return rows


def get_analysis_by_id(aid: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT company_name, website_url, analysis_json, news_json, timestamp FROM competitor_analyses WHERE id=?",
        (aid,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "company_name": row[0], "website_url": row[1],
            "analysis": json.loads(row[2]), "news": json.loads(row[3]),
            "timestamp": row[4]
        }
    return None


def delete_analysis_by_id(aid: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM competitor_analyses WHERE id=?", (aid,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# STREAMLIT PAGE CONFIG & INIT
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Competitive Intelligence Analyzer",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)
init_db()

# ---------------------------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .banner-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2.5rem 2rem; border-radius: 12px; color: white;
        margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center;
    }
    .banner-title  { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; letter-spacing: -0.5px; }
    .banner-subtitle { font-size: 1.1rem; font-weight: 300; opacity: 0.9; }

    .input-card {
        background-color: #f8fafc; border: 1px solid #e2e8f0;
        padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem;
    }
    .section-title {
        color: #1e3c72; font-size: 1.5rem; font-weight: 600;
        border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem;
        margin-top: 1.5rem; margin-bottom: 1rem;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9; border-radius: 6px 6px 0 0;
        padding: 10px 16px; font-weight: 500; color: #475569;
    }
    .stTabs [data-baseweb="tab"]:hover { background-color: #e2e8f0; color: #1e3c72; }
    .stTabs [aria-selected="true"] {
        background-color: #1e3c72 !important; color: white !important; font-weight: 600;
    }

    .metric-box {
        background: white; border: 1px solid #e2e8f0;
        padding: 1rem 1.5rem; border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02); margin-bottom: 1rem;
    }

    div.stButton > button {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white; border: none; padding: 0.6rem 1.8rem; font-weight: 500;
        border-radius: 6px; box-shadow: 0 4px 10px rgba(30,60,114,0.2);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        box-shadow: 0 6px 15px rgba(30,60,114,0.3); transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# BANNER
# ---------------------------------------------------------------------------
st.markdown("""
<div class="banner-container">
    <div class="banner-title">🕵️‍♂️ AI Competitive Intelligence Analyzer</div>
    <div class="banner-subtitle">Scrape website content, pull recent news, and synthesize deep strategic intelligence reports with Gemini 1.5 Flash.</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")

    st.markdown("#### 🔑 API Credentials")
    env_gemini = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
    gemini_key = st.text_input(
        "Google Gemini API Key",
        value=env_gemini or st.session_state.get("gemini_key_input", ""),
        type="password",
        help="Required. Get one free at https://aistudio.google.com/apikey"
    )
    st.session_state["gemini_key_input"] = gemini_key

    env_news = os.getenv("NEWSAPI_API_KEY") or ""
    news_key = st.text_input(
        "NewsAPI Key",
        value=env_news or st.session_state.get("news_key_input", ""),
        type="password",
        help="Optional. Get one free at https://newsapi.org/register"
    )
    st.session_state["news_key_input"] = news_key

    st.markdown("---")
    st.markdown("#### 📂 Analysis History")
    history = get_history()

    if history:
        opts = {f"{r[1]} ({r[3]})": r[0] for r in history}
        sel = st.selectbox("Select past analysis:", ["-- Select --"] + list(opts.keys()))
        if sel != "-- Select --":
            hid = opts[sel]
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Load", key=f"load_{hid}"):
                    hd = get_analysis_by_id(hid)
                    if hd:
                        st.session_state.update({
                            "current_analysis": hd["analysis"],
                            "current_news": hd["news"],
                            "company_name": hd["company_name"],
                            "website_url": hd["website_url"],
                            "timestamp": hd["timestamp"],
                        })
                        st.rerun()
            with c2:
                if st.button("Delete", key=f"del_{hid}"):
                    delete_analysis_by_id(hid)
                    st.success("Deleted.")
                    st.rerun()
    else:
        st.info("No past analyses yet.")

    st.markdown("---")
    st.caption("**AI Competitive Intelligence Analyzer** · Powered by Gemini Flash")

# ---------------------------------------------------------------------------
# SESSION STATE DEFAULTS
# ---------------------------------------------------------------------------
for k in ("current_analysis", "current_news", "company_name", "website_url"):
    if k not in st.session_state:
        st.session_state[k] = None if "analysis" in k or "news" in k else ""

# ---------------------------------------------------------------------------
# INPUT SECTION
# ---------------------------------------------------------------------------
st.markdown('<div class="input-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    comp_name = st.text_input("Competitor Name", value=st.session_state["company_name"], placeholder="e.g. OpenAI")
with c2:
    comp_url = st.text_input("Company Website URL", value=st.session_state["website_url"], placeholder="e.g. https://openai.com")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ANALYZE BUTTON
# ---------------------------------------------------------------------------
if st.button("🚀 Analyze Competitor"):
    st.session_state["current_analysis"] = None
    st.session_state["current_news"] = None

    if not comp_name.strip():
        st.error("Please enter a competitor name.")
    elif not comp_url.strip():
        st.error("Please enter a company website URL.")
    elif not gemini_key.strip():
        st.error("Google Gemini API Key is missing. Configure it in the sidebar.")
    else:
        url = comp_url.strip()
        if not urllib.parse.urlparse(url).scheme:
            url = "https://" + url
        name = comp_name.strip()

        with st.status("🔍 Scraping website content...", expanded=True) as status:
            scraped = scrape_website(url)
            if scraped.startswith("Error"):
                st.warning(f"Scraping issue: {scraped}")
                st.info("Will rely on news articles and model knowledge.")
            else:
                st.write("✅ Website content scraped and cleaned.")

            status.update(label="📰 Fetching recent news articles...", state="running")
            news_res = fetch_company_news(name, news_key)
            articles = []
            if news_res["success"]:
                articles = news_res["articles"]
                st.write(f"✅ Retrieved {len(articles)} news articles.")
            else:
                st.warning(f"News skipped: {news_res['error']}")

            status.update(label="🧠 Analyzing with Gemini...", state="running")
            result = analyze_competitor(name, scraped, articles, gemini_key)

            if result["success"]:
                status.update(label="💾 Saving results...", state="running")
                save_analysis(name, url, result["analysis"], articles)
                st.session_state.update({
                    "current_analysis": result["analysis"],
                    "current_news": articles,
                    "company_name": name,
                    "website_url": url,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                st.success(f"Intelligence report generated for **{name}**!")
                st.rerun()
            else:
                status.update(label="❌ Analysis Failed", state="error", expanded=True)
                st.error(f"Error: {result['error']}")

# ---------------------------------------------------------------------------
# RESULTS DASHBOARD
# ---------------------------------------------------------------------------
if st.session_state["current_analysis"]:
    analysis = st.session_state["current_analysis"]
    news = st.session_state["current_news"] or []
    name = st.session_state["company_name"]
    url = st.session_state["website_url"]
    ts = st.session_state.get("timestamp", "Just now")

    st.markdown("---")

    dc1, dc2 = st.columns([3, 1])
    with dc1:
        st.markdown(f"### 📊 Intelligence Profile: **{name}**")
        st.caption(f"Website: {url} | Generated: {ts}")
    with dc2:
        try:
            pdf = generate_pdf_report(name, url, analysis, news)
            st.download_button(
                "📥 Download PDF Report", data=pdf,
                file_name=f"CI_Report_{name.replace(' ', '_')}.pdf",
                mime="application/pdf", use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

    # Metrics
    st.markdown('<div class="metric-box">', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"**Target**<br><span style='font-size:1.4rem;font-weight:700;color:#1e3c72;'>{name}</span>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"**Data Sources**<br>Web Scrape: ✅ | News: {len(news)} articles", unsafe_allow_html=True)
    with m3:
        st.markdown("**Engine**<br>Gemini Flash · Structured JSON", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tabs
    t1, t2, t3, t4, t5, t6, t7 = st.tabs([
        "🏢 Overview", "🎯 Business Focus", "📈 Trends",
        "💡 Opportunities", "⚠️ Risks", "🔮 Future Path", "📰 News"
    ])
    with t1:
        st.markdown("#### 🏢 Company Overview")
        st.markdown(analysis.get("company_overview", "N/A"))
    with t2:
        st.markdown("#### 🎯 Current Business Focus")
        st.markdown(analysis.get("current_business_focus", "N/A"))
    with t3:
        st.markdown("#### 📈 Hiring & Product Trends")
        st.markdown(analysis.get("hiring_product_trends", "N/A"))
    with t4:
        st.markdown("#### 💡 Market Opportunities")
        st.markdown(analysis.get("market_opportunities", "N/A"))
    with t5:
        st.markdown("#### ⚠️ Potential Risks")
        st.markdown(analysis.get("potential_risks", "N/A"))
    with t6:
        st.markdown("#### 🔮 Predicted Future Direction")
        st.markdown(analysis.get("predicted_future_direction", "N/A"))
    with t7:
        st.markdown("#### 📰 Recent News Coverage")
        if news:
            for art in news:
                st.markdown(f"""
                <div style="background:#f8fafc;border-left:4px solid #3182ce;padding:12px;margin-bottom:12px;border-radius:0 6px 6px 0;">
                    <b style="font-size:1.05rem;color:#2c5282;">{art['title']}</b><br>
                    <span style="font-size:0.85rem;color:#718096;">Source: {art['source']} | {art['date']}</span><br>
                    <p style="margin-top:6px;font-size:0.95rem;color:#2d3748;">{art['description']}</p>
                    <a href="{art['url']}" target="_blank" style="font-size:0.85rem;color:#3182ce;">Read Full Article ↗</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No news articles fetched. Add a NewsAPI key in the sidebar.")

else:
    # Landing / instructions view
    st.info("👈 Enter competitor details above and click 'Analyze Competitor', or load from history.")
    st.markdown("### 🛠 How it works")
    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in [
        (c1, "🌐", "1. Smart Scraping", "Extracts and cleans website text using BeautifulSoup."),
        (c2, "📰", "2. News Integration", "Fetches real-time articles via NewsAPI."),
        (c3, "🧠", "3. Gemini Synthesis", "Synthesizes all data into structured intelligence with Gemini Flash."),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:#f8fafc;padding:20px;border-radius:8px;border:1px solid #e2e8f0;">
                <span style="font-size:2rem;">{icon}</span>
                <h4 style="color:#1e3c72;margin-top:10px;">{title}</h4>
                <p style="color:#4a5568;font-size:0.9rem;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)
