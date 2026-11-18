"""
scraper.py - Upgraded Multi-Page Competitor Website Intelligence Scraper
========================================================================
Performs secure, domain-restricted, multi-page crawling with robust HTML sanitization,
heading extraction, meta-tag parsing, and product signal identification.
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import socket
import ipaddress
from typing import Dict, Any, List

# Common headers to avoid 403 blocks while respecting web etiquette
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def is_safe_url(url: str) -> bool:
    """Validates URL and prevents SSRF to private/internal network addresses."""
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block localhost / link-local / private domains
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0"):
            return False
        # Resolve IP to verify non-private
        try:
            ip = ipaddress.ip_address(socket.gethostbyname(hostname))
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except Exception:
            pass # Continue if DNS resolves differently
        return True
    except Exception:
        return False

def clean_url(url: str) -> str:
    """Normalizes URL with default https:// scheme."""
    url = url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url

def extract_single_page(url: str, timeout: int = 12) -> Dict[str, Any]:
    """Fetches and cleans a single webpage."""
    if not is_safe_url(url):
        return {"error": f"Invalid or unsafe URL: {url}", "url": url}

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"Fetch failed: {str(e)}", "url": url}

    try:
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 1. Page Title
        title = soup.title.string.strip() if (soup.title and soup.title.string) else ""
        
        # 2. Meta Description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)}) or \
                   soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()
            
        # 3. Headings
        headings = []
        for tag in soup.find_all(["h1", "h2", "h3"]):
            text = tag.get_text().strip()
            if text and len(text) > 3 and text not in headings:
                headings.append(text)
        
        # 4. Strip noise
        for element in soup([
            "script", "style", "nav", "footer", "form", "noscript", 
            "iframe", "header", "svg", "button", "aside"
        ]):
            element.decompose()
            
        # 5. Extract structured paragraphs
        paragraphs = []
        for p in soup.find_all(["p", "li"]):
            p_text = p.get_text().strip()
            # Filter low-value snippets
            if len(p_text) > 30 and not any(kw in p_text.lower() for kw in ["cookie", "privacy policy", "terms of use"]):
                paragraphs.append(p_text)
                
        cleaned_text = "\n".join(paragraphs)
        
        # Deduplicate repeating lines
        seen = set()
        deduped = []
        for line in cleaned_text.splitlines():
            line_str = line.strip()
            if line_str and line_str not in seen:
                seen.add(line_str)
                deduped.append(line_str)
        final_text = "\n".join(deduped)

        # 6. Extract internal subpage links for multi-page crawl
        parsed_base = urllib.parse.urlparse(url)
        discovered_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urllib.parse.urljoin(url, href)
            parsed_link = urllib.parse.urlparse(full_url)
            # Ensure same domain and looks like an informative subpage
            if parsed_link.netloc == parsed_base.netloc:
                path = parsed_link.path.lower()
                if any(kw in path for kw in ["about", "product", "solution", "service", "company", "technology", "platform", "features"]):
                    if full_url not in discovered_links and full_url != url:
                        discovered_links.append(full_url)

        return {
            "url": url,
            "title": title,
            "meta_description": meta_desc,
            "headings": headings[:20],
            "content": final_text[:10000],
            "discovered_links": discovered_links[:5],
            "error": None
        }
    except Exception as e:
        return {"error": f"Parsing error: {str(e)}", "url": url}

def scrape_website_multi_page(base_url: str, max_subpages: int = 2) -> Dict[str, Any]:
    """
    Crawls main page + up to max_subpages relevant subpages on the same domain
    for a comprehensive corporate knowledge snapshot.
    """
    clean_base = clean_url(base_url)
    main_res = extract_single_page(clean_base)
    
    if main_res.get("error"):
        return {
            "success": False,
            "base_url": clean_base,
            "error": main_res["error"],
            "combined_text": "",
            "pages": []
        }

    pages = [main_res]
    combined_texts = [
        f"--- PAGE: {main_res.get('title', clean_base)} ({clean_base}) ---\n"
        f"META: {main_res.get('meta_description', '')}\n"
        f"HEADINGS: {', '.join(main_res.get('headings', []))}\n"
        f"{main_res.get('content', '')}"
    ]

    # Scrape 1-2 discovered relevant subpages
    sublinks = main_res.get("discovered_links", [])
    for sublink in sublinks[:max_subpages]:
        sub_res = extract_single_page(sublink, timeout=8)
        if not sub_res.get("error") and len(sub_res.get("content", "")) > 100:
            pages.append(sub_res)
            combined_texts.append(
                f"\n--- SUBPAGE: {sub_res.get('title', sublink)} ({sublink}) ---\n"
                f"{sub_res.get('content', '')[:6000]}"
            )

    full_combined = "\n\n".join(combined_texts)
    # Cap total combined text at 22,000 characters to keep memory & model inference fast
    if len(full_combined) > 22000:
        full_combined = full_combined[:22000] + "\n[Content truncated for length]"

    return {
        "success": True,
        "base_url": clean_base,
        "title": main_res.get("title", ""),
        "meta_description": main_res.get("meta_description", ""),
        "pages": pages,
        "combined_text": full_combined,
        "error": None
    }

def scrape_website(url: str) -> str:
    """Legacy backward-compatible wrapper returning string."""
    res = scrape_website_multi_page(url, max_subpages=1)
    if res["success"]:
        return res["combined_text"]
    return f"Error: {res.get('error', 'Scraping failed')}"
