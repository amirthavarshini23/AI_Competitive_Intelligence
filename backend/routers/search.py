"""
routers/search.py - RAG Semantic Search Router
==============================================
"""

from fastapi import APIRouter, HTTPException
from schemas.models import SemanticSearchRequest
from services.semantic_search import answer_rag_question

router = APIRouter(tags=["Search"])

@router.post("/api/search/semantic")
def search_semantic_knowledge(req: SemanticSearchRequest):
    """
    Retrieval-Augmented Generation (RAG) search across indexed competitor documents.
    Returns synthesized answer, evidence chunks, and citations.
    """
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty.")

    try:
        result = answer_rag_question(
            query=req.query.strip(),
            competitor_id=req.competitor_id,
            top_k=req.top_k or 5
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Semantic search failed: {str(e)}")
