"""
scraper.py - Website Text Scraper
==================================
Scrapes and cleans text content from a competitor's website using
requests and BeautifulSoup. Handles timeouts, SSL errors, and
connection failures gracefully.
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse


def scrape_website(url: str) -> str:
    """
    Scrapes the text content of a given website URL.

    Args:
        url: The target website URL.

    Returns:
        Cleaned plain text content or an error message string.
    """
    # Auto-prepend scheme if missing
    parsed_url = urllib.parse.urlparse(url)
    if not parsed_url.scheme:
        url = "https://" + url
        parsed_url = urllib.parse.urlparse(url)

    if not parsed_url.netloc:
        return "Error: Invalid URL format."

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return f"Error: The request to {url} timed out (10s limit)."
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to {url}. Please verify the URL and your network."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP exception occurred: {e}"
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to retrieve content: {e}"

    try:
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise elements
        for element in soup([
            "script", "style", "head", "title", "meta", "[document]",
            "noscript", "iframe", "form", "nav", "footer"
        ]):
            element.decompose()

        # Extract and clean text
        text_content = soup.get_text(separator="\n")
        lines = [line.strip() for line in text_content.splitlines()]
        clean_lines = [line for line in lines if line]
        cleaned_text = "\n".join(clean_lines)

        # Truncate to keep token usage manageable
        max_chars = 12000
        if len(cleaned_text) > max_chars:
            cleaned_text = cleaned_text[:max_chars] + "\n\n[Content truncated due to length...]"

        return cleaned_text if cleaned_text.strip() else \
            "Error: No visible text content could be extracted from this website."

    except Exception as e:
        return f"Error parsing website content: {str(e)}"


if __name__ == "__main__":
    test_url = "https://example.com"
    print(f"Testing scraper on {test_url}...")
    result = scrape_website(test_url)
    print(result[:300])
