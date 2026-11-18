"""
ollama_service.py - Local LLM Engine (Ollama Integration)
=========================================================
Integrates local LLMs (Qwen 2.5, Llama 3, Mistral) via Ollama's REST API.
Handles connection health, model inventory, structured JSON generation,
and clean fallback when Ollama is offline.
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("OllamaService")

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:3b"

def check_ollama_status() -> Dict[str, Any]:
    """
    Checks if Ollama service is reachable and lists installed models.
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {
                "running": True,
                "models": models,
                "default_model": DEFAULT_MODEL,
                "has_default_model": any(DEFAULT_MODEL in m for m in models),
                "error": None
            }
    except requests.exceptions.RequestException as e:
        return {
            "running": False,
            "models": [],
            "default_model": DEFAULT_MODEL,
            "has_default_model": False,
            "error": "Ollama service is not running or unreachable at localhost:11434"
        }
    except Exception as e:
        return {
            "running": False,
            "models": [],
            "default_model": DEFAULT_MODEL,
            "has_default_model": False,
            "error": str(e)
        }

def query_ollama_json(prompt: str, model_name: str = DEFAULT_MODEL, timeout: int = 45) -> Dict[str, Any]:
    """
    Sends a structured prompt to Ollama requesting strict JSON output.
    Returns: {"success": bool, "data": dict, "raw": str, "error": str|None}
    """
    status = check_ollama_status()
    if not status["running"]:
        return {
            "success": False,
            "data": {},
            "raw": "",
            "error": "Ollama is not running. Please start Ollama or rely on Extractive NLP mode."
        }

    # If the requested model is not installed, use the first available model if any
    available_models = status.get("models", [])
    if available_models and not any(model_name in m for m in available_models):
        model_name = available_models[0]

    payload = {
        "model": model_name,
        "prompt": prompt,
        "format": "json",
        "stream": False,
        "options": {
            "temperature": 0.2, # Low temperature for analytical consistency
            "num_predict": 1500
        }
    }

    try:
        resp = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=timeout)
        if resp.status_code != 200:
            return {
                "success": False,
                "data": {},
                "raw": resp.text,
                "error": f"Ollama HTTP {resp.status_code}: {resp.text[:200]}"
            }

        result = resp.json()
        raw_text = result.get("response", "").strip()

        # Parse JSON
        parsed = json.loads(raw_text)
        return {
            "success": True,
            "data": parsed,
            "raw": raw_text,
            "model_used": model_name,
            "error": None
        }

    except json.JSONDecodeError as e:
        # Fallback regex extraction if Ollama included markdown around JSON
        try:
            import re
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return {
                    "success": True,
                    "data": parsed,
                    "raw": raw_text,
                    "model_used": model_name,
                    "error": None
                }
        except Exception:
            pass
        return {
            "success": False,
            "data": {},
            "raw": raw_text,
            "error": f"Failed to parse Ollama JSON response: {str(e)}"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "data": {},
            "raw": "",
            "error": f"Ollama generation timed out ({timeout}s). Try a smaller model like qwen2.5:1.5b."
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "raw": "",
            "error": f"Ollama request error: {str(e)}"
        }
