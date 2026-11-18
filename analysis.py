"""
analysis.py - Gemini AI Competitive Analysis Engine
=====================================================
Combines scraped website text and news articles into a detailed prompt,
then uses Google Gemini with structured JSON output (response_schema)
to generate 6 intelligence sections. Includes dynamic model detection
to automatically resolve model availability issues.
"""

import os
import json
import google.generativeai as genai
import typing_extensions as typing


# Strict JSON schema enforced on Gemini output
class CompetitorAnalysis(typing.TypedDict):
    company_overview: str
    current_business_focus: str
    hiring_product_trends: str
    market_opportunities: str
    potential_risks: str
    predicted_future_direction: str


def _resolve_model_name(preferred: str = "gemini-1.5-flash") -> str:
    """
    Dynamically queries genai.list_models() to find the best available
    model. Falls back through several candidates if the preferred model
    is not available for the user's API key or region.
    """
    try:
        available = [m.name.replace("models/", "") for m in genai.list_models()]

        # Ordered preference list
        candidates = [
            preferred,
            "gemini-1.5-flash-latest",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
        ]

        for name in candidates:
            if name in available:
                return name

        # If none of our preferred names matched, pick any flash/pro model
        flash_or_pro = [n for n in available if "flash" in n or "pro" in n]
        if flash_or_pro:
            return flash_or_pro[0]

        # Absolute last resort
        if available:
            return available[0]

    except Exception:
        pass  # list_models failed; fall through to default

    return preferred


def analyze_competitor(
    company_name: str,
    website_content: str,
    news_articles: list,
    api_key: str = None
) -> dict:
    """
    Analyzes combined website text and news articles using Google Gemini.

    Args:
        company_name: Name of the competitor.
        website_content: Scraped text from the competitor's website.
        news_articles: List of news article dicts from news_agent.py.
        api_key: Gemini / Google API key.

    Returns:
        dict with keys: success (bool), analysis (dict), error (str|None).
    """
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key or api_key.strip() == "":
        return {
            "success": False, "analysis": {},
            "error": "Google Gemini API key is missing. Please configure it in the sidebar."
        }

    # Format news articles for the prompt
    news_text = ""
    if news_articles:
        for idx, art in enumerate(news_articles, 1):
            news_text += (
                f"Article {idx}:\n"
                f"Title: {art.get('title')}\n"
                f"Source: {art.get('source')} | Date: {art.get('date')}\n"
                f"Summary: {art.get('description')}\n"
                f"Link: {art.get('url')}\n"
                f"Content Snippet: {art.get('content')}\n"
                f"{'-' * 40}\n"
            )
    else:
        news_text = "No recent news articles were found for this company."

    prompt = f"""
You are a top-tier Competitive Intelligence Analyst.
Analyze the following collected data for the competitor: "{company_name}".

--- WEBSITE CONTENT ---
{website_content}

--- RECENT NEWS ARTICLES ---
{news_text}

--- ANALYSIS INSTRUCTIONS ---
Using only the website content and news articles provided above, perform a deep
competitive intelligence analysis. Generate detailed, rich, and objective insights
for each of the following sections:

1. **Company Overview**: Who they are, their mission, and general positioning.
2. **Current Business Focus**: Products, services, or core value propositions they emphasize.
3. **Hiring/Product Trends**: Expansion signs, new features, launches, job trends, or tech shifts (mention if none are detectable).
4. **Market Opportunities**: Areas well-positioned to expand, unserved niches, or strategic advantages.
5. **Potential Risks**: Vulnerabilities, market challenges, product issues, or threats.
6. **Predicted Future Direction**: A forward-looking 12-24 month projection of strategy and likely moves.

Format each section's value as high-quality Markdown text with lists, bold keywords,
and callouts where appropriate.
"""

    try:
        genai.configure(api_key=api_key)

        # Dynamically resolve the best available model
        model_name = _resolve_model_name("gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)

        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=CompetitorAnalysis,
            temperature=0.2,
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )

        result_json = json.loads(response.text)
        return {"success": True, "analysis": result_json, "error": None}

    except json.JSONDecodeError as e:
        return {
            "success": False, "analysis": {},
            "error": f"Failed to parse Gemini JSON: {str(e)}. Raw: {response.text[:500]}"
        }
    except Exception as e:
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
            error_msg = "Invalid Google Gemini API key. Please check your key."
        return {
            "success": False, "analysis": {},
            "error": f"Gemini API Error: {error_msg}"
        }


if __name__ == "__main__":
    test_key = os.getenv("GEMINI_API_KEY")
    if test_key:
        print("Testing Gemini analysis...")
        res = analyze_competitor(
            company_name="Acme Corp",
            website_content="Acme Corp makes high quality gadgets. Based in the desert.",
            news_articles=[{
                "title": "Acme Corp stocks soar",
                "source": "WSJ", "date": "Nov 18, 2026",
                "description": "Stocks up after record quarter."
            }],
            api_key=test_key
        )
        print("Success:", res["success"])
        if res["success"]:
            print(json.dumps(res["analysis"], indent=2))
        else:
            print("Error:", res["error"])
    else:
        print("No GEMINI_API_KEY found; skipping debug run.")
