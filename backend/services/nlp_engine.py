"""
nlp_engine.py - Local NLP, Sentiment, Keyword & Extractive Intelligence Engine
=============================================================================
Provides offline, deterministic NLP processing using TF-IDF, NLTK VADER sentiment,
extractive summarization, and key-term clustering without external API costs.
"""

import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize NLTK VADER sentiment analyzer if available
try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    vader = SentimentIntensityAnalyzer()
except Exception:
    vader = None

# Curated business & tech stop words
ENGLISH_STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
    "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've",
    "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only",
    "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's",
    "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "click",
    "privacy", "cookies", "terms", "rights", "reserved", "copyright", "home", "contact"
])

def clean_text(text: str) -> str:
    """Normalizes whitespace and removes unprintable characters."""
    if not text:
        return ""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Computes sentiment using VADER.
    Returns: {"label": "positive"|"negative"|"neutral", "compound": float, "pos": float, "neg": float}
    """
    if not text or not text.strip():
        return {"label": "neutral", "compound": 0.0, "pos": 0.0, "neg": 0.0}

    if vader:
        scores = vader.polarity_scores(text)
        compound = scores["compound"]
        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"
        return {
            "label": label,
            "compound": round(compound, 3),
            "pos": round(scores["pos"], 3),
            "neg": round(scores["neg"], 3)
        }
    
    # Simple rule-based fallback if VADER is unavailable
    pos_words = {"growth", "profit", "innovative", "leader", "expanded", "success", "breakthrough", "launch", "partner", "award"}
    neg_words = {"lawsuit", "decline", "drop", "failure", "breach", "fine", "loss", "risk", "cut", "warning"}
    tokens = set(re.findall(r"\b[a-z]{3,}\b", text.lower()))
    pos_count = len(tokens.intersection(pos_words))
    neg_count = len(tokens.intersection(neg_words))
    
    if pos_count > neg_count:
        return {"label": "positive", "compound": 0.35, "pos": 0.4, "neg": 0.1}
    elif neg_count > pos_count:
        return {"label": "negative", "compound": -0.35, "pos": 0.1, "neg": 0.4}
    return {"label": "neutral", "compound": 0.0, "pos": 0.1, "neg": 0.1}

def extract_top_keywords(text: str, top_n: int = 15) -> List[Dict[str, Any]]:
    """
    Extracts top keywords and 2-gram phrases using TF-IDF weighting.
    """
    if not text or len(text.split()) < 5:
        return []

    try:
        vectorizer = TfidfVectorizer(
            stop_words=list(ENGLISH_STOPWORDS),
            ngram_range=(1, 2),
            max_features=100
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        
        # Sort terms by score
        ranked_indices = np.argsort(scores)[::-1]
        results = []
        for idx in ranked_indices:
            term = feature_names[idx]
            # Skip single digit numbers or tiny fragments
            if len(term) > 2 and not term.isnumeric():
                results.append({"term": term, "score": round(float(scores[idx]), 4)})
            if len(results) >= top_n:
                break
        return results
    except Exception:
        return []

def extract_key_sentences(text: str, query_terms: List[str] = None, max_sentences: int = 4) -> List[str]:
    """
    Extracts the most salient sentences using TF-IDF scoring and optional query bias.
    Guarantees grounded, factual summaries extracted directly from source text.
    """
    if not text:
        return []

    # Split into clean sentences
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 35 and not s.strip().startswith("http")]

    if not sentences:
        return []

    if len(sentences) <= max_sentences:
        return sentences

    try:
        vectorizer = TfidfVectorizer(stop_words=list(ENGLISH_STOPWORDS))
        matrix = vectorizer.fit_transform(sentences)
        
        if query_terms:
            # Score sentences relative to query terms
            query_vec = vectorizer.transform([" ".join(query_terms)])
            scores = cosine_similarity(matrix, query_vec).flatten()
        else:
            # Score sentences by their centrality to the overall document
            doc_vec = matrix.mean(axis=0)
            scores = cosine_similarity(matrix, doc_vec).flatten()

        top_indices = np.argsort(scores)[::-1][:max_sentences]
        # Preserve original narrative order
        top_indices = sorted(top_indices)
        return [sentences[i] for i in top_indices]
    except Exception:
        return sentences[:max_sentences]

def extract_products_and_services(text: str) -> List[str]:
    """Detects product and feature patterns from scraped headings and text."""
    detected = set()
    
    # Regex patterns for products, platforms, tools, APIs
    patterns = [
        r"\b([A-Z][a-zA-Z0-9]+(?:\s[A-Z][a-zA-Z0-9]+)?\s(?:Platform|Cloud|API|Suite|Studio|Engine|Pro|Enterprise|AI|OS|Server|365|Workspace))\b",
        r"(?:products?|solutions?|services?)\s*(?:include|such as|like)\s*([A-Za-z0-9,\s–-]+(?:\.|\n))",
    ]
    
    for pat in patterns:
        for match in re.finditer(pat, text):
            match_str = match.group(1).strip().rstrip(".,;")
            if 3 < len(match_str) < 60:
                detected.add(match_str)
                
    return sorted(list(detected))[:10]
