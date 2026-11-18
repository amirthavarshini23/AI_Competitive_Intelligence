"""
db.py - SQLite Database Management & Schemas
============================================
Handles connection pooling, table schemas, initialization, and transactions.
"""

import sqlite3
import os
from contextlib import contextmanager

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "competitors.db")

@contextmanager
def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initializes all database tables with indexes and foreign keys."""
    with get_db() as conn:
        cursor = conn.cursor()

        # 1. Competitors Registry
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                website_url TEXT NOT NULL,
                domain TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Strategic Analyses (6 Pillars + SWOT + Scores)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                company_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                swot_json TEXT NOT NULL DEFAULT '{}',
                strategic_scores_json TEXT NOT NULL DEFAULT '{}',
                engine_used TEXT NOT NULL DEFAULT 'Extractive NLP',
                model_name TEXT NOT NULL DEFAULT 'rule_based',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 3. Scraped Documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                url TEXT NOT NULL,
                title TEXT,
                meta_description TEXT,
                headings_json TEXT DEFAULT '[]',
                content TEXT NOT NULL,
                char_count INTEGER DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 4. News Articles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                published_date TEXT,
                url TEXT,
                description TEXT,
                content TEXT,
                sentiment TEXT DEFAULT 'neutral',
                sentiment_score REAL DEFAULT 0.0,
                topics_json TEXT DEFAULT '[]',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 5. Embeddings & Document Chunks Metadata (for Semantic Search / RAG)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER,
                doc_id INTEGER,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                vector_json TEXT,
                source_url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 6. Competitor Snapshots (for Change Monitoring)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitor_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                website_url TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                text_sample TEXT,
                keywords_json TEXT DEFAULT '[]',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 7. Detected Changes Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detected_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_summary TEXT NOT NULL,
                new_keywords_json TEXT DEFAULT '[]',
                detected_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                viewed INTEGER DEFAULT 0,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 8. Monitoring Jobs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS monitoring_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL UNIQUE,
                company_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                check_interval_minutes INTEGER DEFAULT 60,
                last_checked DATETIME,
                next_check DATETIME,
                is_active INTEGER DEFAULT 1,
                status TEXT DEFAULT 'idle',
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE
            )
        """)

        # 9. Analysis History & Metrics Tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competitor_id INTEGER NOT NULL,
                analysis_id INTEGER NOT NULL,
                metric_snapshots_json TEXT DEFAULT '{}',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (competitor_id) REFERENCES competitors(id) ON DELETE CASCADE,
                FOREIGN KEY (analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
            )
        """)

        # 10. Legacy table compatibility
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS competitor_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                website_url TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                news_json TEXT NOT NULL,
                scraped_content TEXT DEFAULT '',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for optimal query speeds
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comp_name ON competitors(name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_comp ON analyses(competitor_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_comp ON news_articles(competitor_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_emb_comp ON embeddings_metadata(competitor_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mon_active ON monitoring_jobs(is_active);")
