"""
semantic_search.py - RAG Pipeline & Semantic Knowledge Retrieval
================================================================
Handles document chunking, vector embedding, similarity retrieval,
and evidence-backed Question Answering over scraped competitor knowledge.
"""

import json
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database.db import get_db
from services.ollama_service import query_ollama_json, check_ollama_status

def chunk_text(text: str, chunk_size: int = 450, overlap: int = 60) -> List[str]:
    """Divides text into overlapping semantic passages."""
    if not text:
        return []

    # Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split(" ")
    chunks = []
    
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        if end == len(words):
            break
        start += (chunk_size - overlap)

    return chunks

def index_competitor_content(competitor_id: int, source_url: str, text: str):
    """
    Chunks document and stores in SQLite embeddings_metadata table.
    """
    chunks = chunk_text(text, chunk_size=80, overlap=15)
    if not chunks:
        return

    with get_db() as conn:
        # Clear previous chunks for this competitor to avoid duplicates
        conn.execute("DELETE FROM embeddings_metadata WHERE competitor_id = ?", (competitor_id,))
        for idx, chunk in enumerate(chunks):
            conn.execute(
                """INSERT INTO embeddings_metadata 
                   (competitor_id, chunk_index, chunk_text, source_url) 
                   VALUES (?, ?, ?, ?)""",
                (competitor_id, idx, chunk, source_url)
            )

def search_semantic_chunks(query: str, competitor_id: Optional[int] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs cosine similarity retrieval over indexed chunks.
    """
    with get_db() as conn:
        if competitor_id:
            rows = conn.execute(
                """SELECT em.id, em.competitor_id, c.name as company_name, em.chunk_index, 
                          em.chunk_text, em.source_url 
                   FROM embeddings_metadata em
                   JOIN competitors c ON c.id = em.competitor_id
                   WHERE em.competitor_id = ?""",
                (competitor_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT em.id, em.competitor_id, c.name as company_name, em.chunk_index, 
                          em.chunk_text, em.source_url 
                   FROM embeddings_metadata em
                   JOIN competitors c ON c.id = em.competitor_id"""
            ).fetchall()

    if not rows:
        return []

    corpus = [r["chunk_text"] for r in rows]
    
    try:
        # L2-normalized TF-IDF vectorizer with n-grams
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
        tfidf_matrix = vectorizer.fit_transform(corpus)
        query_vec = vectorizer.transform([query])
        
        sims = cosine_similarity(query_vec, tfidf_matrix).flatten()
        top_indices = np.argsort(sims)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(sims[idx])
            # Only include relevant matches (threshold > 0.05)
            if score > 0.02:
                row = rows[idx]
                results.append({
                    "id": row["id"],
                    "competitor_id": row["competitor_id"],
                    "company_name": row["company_name"],
                    "chunk_text": row["chunk_text"],
                    "source_url": row["source_url"],
                    "similarity_score": round(score, 3)
                })
        return results

    except Exception:
        return []

def answer_rag_question(query: str, competitor_id: Optional[int] = None, top_k: int = 5) -> Dict[str, Any]:
    """
    Evidence-grounded Question Answering.
    Synthesizes answer using local Ollama LLM if available; otherwise uses extractive NLP synthesis.
    """
    matches = search_semantic_chunks(query, competitor_id=competitor_id, top_k=top_k)
    
    if not matches:
        return {
            "query": query,
            "answer": "No indexed content found matching this query. Please analyze this competitor first to populate their knowledge base.",
            "sources": [],
            "confidence": "Low",
            "engine": "Knowledge Retrieval"
        }

    # Format evidence context
    context_passages = []
    for i, m in enumerate(matches, 1):
        context_passages.append(f"[{i}] (Company: {m['company_name']} | URL: {m['source_url']})\n{m['chunk_text']}")
    context_str = "\n\n".join(context_passages)

    # Check if Ollama is running
    ollama_status = check_ollama_status()
    if ollama_status["running"]:
        prompt = f"""
You are an evidence-based Competitive Intelligence Analyst.
Answer the following question using ONLY the retrieved facts from the competitor documents provided below.
Do not assume or invent facts. Cite source numbers like [1], [2] when referencing facts.
If the provided passages do not contain sufficient info, explicitly state: "Insufficient information in collected documents."

QUESTION: {query}

RETRIEVED EVIDENCE PASSAGES:
{context_str}

Respond in strict JSON with the following format:
{{
    "answer": "Concise, factual answer citing [1], [2]...",
    "key_takeaways": ["point 1", "point 2"],
    "confidence": "High" | "Medium" | "Low"
}}
"""
        res = query_ollama_json(prompt, model_name=ollama_status.get("models", ["qwen2.5:3b"])[0])
        if res["success"] and isinstance(res["data"], dict) and "answer" in res["data"]:
            return {
                "query": query,
                "answer": res["data"].get("answer", ""),
                "key_takeaways": res["data"].get("key_takeaways", []),
                "confidence": res["data"].get("confidence", "Medium"),
                "sources": matches,
                "engine": f"RAG + Ollama ({res.get('model_used', 'Local LLM')})"
            }

    # Extractive Fallback: Synthesize grounded response directly from highest-scoring passages
    best_chunk = matches[0]
    sentences = re.split(r"(?<=[.!?])\s+", best_chunk["chunk_text"])
    summary_sentence = sentences[0] if sentences else best_chunk["chunk_text"][:200]
    
    answer_text = (
        f"Based on the collected corporate documentation for **{best_chunk['company_name']}**:\n\n"
        f"> \"{summary_sentence}\"\n\n"
        f"Key evidence retrieved with similarity score **{best_chunk['similarity_score']}** "
        f"from source: {best_chunk['source_url']}."
    )

    return {
        "query": query,
        "answer": answer_text,
        "key_takeaways": [m["chunk_text"][:120] + "..." for m in matches[:3]],
        "confidence": "Medium (Extractive Semantic Match)",
        "sources": matches,
        "engine": "Extractive Semantic RAG (Offline)"
    }
