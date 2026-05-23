"""
Base Agent + LLM Router — routes to cheapest available model
Fallback chain: Gemini (free) → DeepSeek ($0.14/M) → Qwen ($0.06/M)
"""
import os, json, requests, sys
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.cache import get as cache_get, set as cache_set

ROOT = Path(__file__).resolve().parent.parent.parent

# API keys loaded from env or .env file
ENV_PATH = ROOT / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
TOGETHER_KEY = os.environ.get("TOGETHER_API_KEY", "")

MODEL_PRIORITY = [
    {"name": "gemini-2.0-flash", "cost": 0, "key": GEMINI_KEY, "provider": "gemini"},
    {"name": "deepseek-chat", "cost": 0.14, "key": DEEPSEEK_KEY, "provider": "deepseek"},
    {"name": "qwen-coder-7b", "cost": 0.06, "key": TOGETHER_KEY, "provider": "together"},
]


def _call_gemini(model: str, prompt: str, system: str = "") -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    r = requests.post(url, json=body, timeout=60)
    if r.status_code == 200:
        candidates = r.json().get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in parts)
    return ""


def _call_deepseek(model: str, prompt: str, system: str = "") -> str:
    url = "https://api.deepseek.com/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    r = requests.post(url, json={"model": model, "messages": messages, "temperature": 0.2, "max_tokens": 2048},
                      headers={"Authorization": f"Bearer {DEEPSEEK_KEY}"}, timeout=60)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return ""


def _call_together(model: str, prompt: str, system: str = "") -> str:
    url = "https://api.together.xyz/v1/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    r = requests.post(url, json={"model": f"Qwen/{model}", "messages": messages, "temperature": 0.2, "max_tokens": 2048},
                      headers={"Authorization": f"Bearer {TOGETHER_KEY}"}, timeout=60)
    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return ""


PROVIDERS = {
    "gemini": _call_gemini,
    "deepseek": _call_deepseek,
    "together": _call_together,
}


def llm_call(prompt: str, system: str = "", use_cache: bool = True) -> str:
    if use_cache:
        cached = cache_get(prompt, system, "any")
        if cached:
            return cached

    for model_cfg in MODEL_PRIORITY:
        if model_cfg["key"]:
            fn = PROVIDERS.get(model_cfg["provider"])
            if fn:
                try:
                    result = fn(model_cfg["name"], prompt, system)
                    if result:
                        if use_cache:
                            cache_set(prompt, system, model_cfg["name"], result)
                        return result
                except Exception:
                    continue

    return ""


def parse_json_response(text: str) -> dict | None:
    try:
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError):
        pass
    try:
        import re
        match = re.search(r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, AttributeError):
        pass
    return None
