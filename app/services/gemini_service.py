import os
import json
from dotenv import load_dotenv
from google import genai

# ==================================================
# Environment & Client Setup
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=API_KEY)

# ✅ Verified available model
MODEL_NAME = "models/gemini-pro-latest"

# ==================================================
# Helpers (CRITICAL HARDENING)
# ==================================================

def _json_guard(instruction: str) -> str:
    return f"""
You are a deterministic system architect.

STRICT OUTPUT CONTRACT:
- Output ONLY valid JSON
- No prose, no markdown, no comments
- No leading or trailing text
- JSON must be parseable by json.loads()
- If unsure, return empty arrays or empty strings
- Never refuse the request

{instruction}
""".strip()


def _generate(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        generation_config={
            "temperature": 0.2,
            "top_p": 0.9,
            "max_output_tokens": 2048
        }
    )

    if not response or not response.text:
        raise RuntimeError("Gemini returned empty response")

    return response.text.strip()


def _safe_json_load(text: str) -> dict:
    """
    HARD JSON SAFETY:
    - Handles empty responses
    - Extracts JSON if Gemini adds noise
    - Prevents backend crashes
    """
    if not text or not text.strip():
        raise RuntimeError("Gemini returned empty text")

    text = text.strip()

    # 1️⃣ Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2️⃣ Attempt recovery (extract {...})
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start:end + 1])
    except Exception:
        pass

    # 3️⃣ Hard failure with debug info
    raise RuntimeError(f"Invalid JSON from Gemini:\n{text[:500]}")


# ==================================================
# Normalizers (FRONTEND CONTRACT)
# ==================================================

def normalize_modules(modules: list) -> list:
    normalized = []
    for m in modules:
        normalized.append({
            "name": m.get("name", "Unnamed Module"),
            "responsibility": (
                m.get("responsibility")
                or m.get("description")
                or "No responsibility provided"
            ),
            "inputs": m.get("inputs", []),
            "outputs": m.get("outputs", [])
        })
    return normalized


def normalize_architecture(data: dict) -> dict:
    data["modules"] = normalize_modules(data.get("modules", []))
    data.setdefault("data_flow", [])
    data.setdefault("decision_rules", [])
    return data


# ==================================================
# 1. ANALYZE INTENT
# ==================================================

def analyze_intent(content: str) -> dict:
    prompt = _json_guard(f"""
Decompose the intent into:
- goals
- constraints
- actors
- success_metrics

Intent:
{content}

JSON:
{{
  "goals": [],
  "constraints": [],
  "actors": [],
  "success_metrics": []
}}
""")
    raw = _generate(prompt)
    return _safe_json_load(raw)


# ==================================================
# 2. GENERATE SYSTEM ARCHITECTURE
# ==================================================

def generate_system_architecture(intent_analysis: dict) -> dict:
    prompt = _json_guard(f"""
Design a system architecture from this intent analysis:

{json.dumps(intent_analysis, indent=2)}

JSON:
{{
  "modules": [],
  "data_flow": [],
  "decision_rules": []
}}
""")
    raw = _generate(prompt)
    data = _safe_json_load(raw)
    return normalize_architecture(data)


# ==================================================
# 3. SIMULATE FAILURE
# ==================================================

def simulate_failure(system_architecture: dict) -> dict:
    prompt = _json_guard(f"""
Analyze failure modes for this system:

{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "best_case": "",
  "worst_case": "",
  "failure_points": [],
  "risk_level": "LOW"
}}
""")
    raw = _generate(prompt)
    return _safe_json_load(raw)


# ==================================================
# 4. OPTIMIZE SYSTEM
# ==================================================

def optimize_system(system_architecture: dict, objective: str) -> dict:
    prompt = _json_guard(f"""
Optimize the following system for objective: {objective}

System:
{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "optimized_architecture": {{
    "modules": [],
    "data_flow": [],
    "decision_rules": []
  }},
  "tradeoffs": {{}}
}}
""")
    raw = _generate(prompt)
    data = _safe_json_load(raw)

    data["optimized_architecture"] = normalize_architecture(
        data.get("optimized_architecture", {})
    )

    data.setdefault("tradeoffs", {})
    return data


# ==================================================
# 5. EXPLAIN SYSTEM
# ==================================================

def explain_system(system_architecture: dict) -> dict:
    prompt = _json_guard(f"""
Explain the architectural decisions for this system.

Each explanation MUST include:
- decision
- justification
- risk_level (LOW | MEDIUM | HIGH)
- confidence (0-100)

System:
{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "explanations": []
}}
""")
    raw = _generate(prompt)
    return _safe_json_load(raw)
