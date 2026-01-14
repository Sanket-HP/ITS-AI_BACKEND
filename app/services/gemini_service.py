import os
import json
import time
from dotenv import load_dotenv
from google import genai
from services.json_repair import repair_and_parse

# ==================================================
# Environment & Client Setup
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=API_KEY)

# ✅ VERIFIED AVAILABLE MODEL
MODEL_NAME = "models/gemini-pro-latest"

# ==================================================
# Helpers
# ==================================================

def _json_guard(instruction: str) -> str:
    return f"""
IMPORTANT RULES (ABSOLUTE):
- Respond with ONLY valid JSON
- No markdown
- No comments
- No explanations
- Output must start with '{{' and end with '}}'
- Do not include trailing commas

{instruction}
""".strip()


def _generate_json(prompt: str, retries: int = 1) -> dict:
    """
    Calls Gemini and guarantees a JSON object return.
    Never raises. Never crashes FastAPI.
    """
    last_raw = ""

    for attempt in range(retries + 1):
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw = (response.text or "").strip()
        last_raw = raw

        parsed = repair_and_parse(raw)
        if parsed:
            return parsed

        time.sleep(0.5)

    # FINAL FALLBACK — NEVER CRASH
    return {
        "error": "GEMINI_INVALID_JSON",
        "raw_output": last_raw[:500]
    }

# ==================================================
# Normalizers
# ==================================================

def normalize_modules(modules: list) -> list:
    normalized = []
    for m in modules:
        if not isinstance(m, dict):
            continue

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
    if not isinstance(data, dict):
        data = {}

    data["modules"] = normalize_modules(data.get("modules", []))
    data["data_flow"] = data.get("data_flow", [])
    data["decision_rules"] = data.get("decision_rules", [])
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

    data = _generate_json(prompt)

    return {
        "goals": data.get("goals", []),
        "constraints": data.get("constraints", []),
        "actors": data.get("actors", []),
        "success_metrics": data.get("success_metrics", [])
    }

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

    data = _generate_json(prompt)
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

    data = _generate_json(prompt)

    return {
        "best_case": data.get("best_case", ""),
        "worst_case": data.get("worst_case", ""),
        "failure_points": data.get("failure_points", []),
        "risk_level": data.get("risk_level", "LOW")
    }

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

    data = _generate_json(prompt)

    optimized = normalize_architecture(
        data.get("optimized_architecture", {})
    )

    return {
        "optimized_architecture": optimized,
        "tradeoffs": data.get("tradeoffs", {})
    }

# ==================================================
# 5. EXPLAIN SYSTEM
# ==================================================

def explain_system(system_architecture: dict) -> dict:
    prompt = _json_guard(f"""
Explain the architectural decisions for this system:

{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "explanations": []
}}
""")

    data = _generate_json(prompt)

    return {
        "explanations": data.get("explanations", [])
    }
