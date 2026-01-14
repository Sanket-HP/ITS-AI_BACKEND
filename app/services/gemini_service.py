import os
import json
import time
from dotenv import load_dotenv
from google import genai
from app.services.json_repair import repair_and_parse

# ==================================================
# Environment & Client Setup
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=API_KEY)

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
    last_raw = ""

    for _ in range(retries + 1):
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
            "responsibility": m.get("responsibility") or m.get("description", ""),
            "inputs": m.get("inputs", []),
            "outputs": m.get("outputs", [])
        })
    return normalized


def normalize_architecture(data: dict) -> dict:
    if not isinstance(data, dict):
        data = {}

    return {
        "modules": normalize_modules(data.get("modules", [])),
        "data_flow": data.get("data_flow", []),
        "decision_rules": data.get("decision_rules", [])
    }

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
# (FIX: force inputs/outputs early)
# ==================================================

def generate_system_architecture(intent_analysis: dict) -> dict:
    prompt = _json_guard(f"""
Design a system architecture from this intent analysis.
Every module MUST include inputs and outputs.

Intent:
{json.dumps(intent_analysis, indent=2)}

JSON:
{{
  "modules": [
    {{
      "name": "",
      "responsibility": "",
      "inputs": [],
      "outputs": []
    }}
  ],
  "data_flow": [],
  "decision_rules": []
}}
""")

    data = _generate_json(prompt)
    return normalize_architecture(data)

# ==================================================
# 3. SIMULATE FAILURE
# (FIX: component-aware failures)
# ==================================================

def simulate_failure(system_architecture: dict) -> dict:
    prompt = _json_guard(f"""
Analyze failure modes for this system.
Each failure MUST reference a specific module.

System:
{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "failure_points": [
    {{
      "component": "",
      "failure": "",
      "impact": "",
      "severity": "LOW|MEDIUM|HIGH"
    }}
  ],
  "overall_risk": "LOW|MEDIUM|HIGH"
}}
""")

    data = _generate_json(prompt)

    failures = []
    for f in data.get("failure_points", []):
        failures.append({
            "component": f.get("component", "Unknown"),
            "failure": f.get("failure", ""),
            "impact": f.get("impact", ""),
            "severity": f.get("severity", "MEDIUM")
        })

    return {
        "failure_points": failures,
        "overall_risk": data.get("overall_risk", "MEDIUM")
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

    return {
        "optimized_architecture": normalize_architecture(
            data.get("optimized_architecture", {})
        ),
        "tradeoffs": data.get("tradeoffs", {})
    }

# ==================================================
# 5. EXPLAIN SYSTEM
# (FIX: real explainable AI output)
# ==================================================

def explain_system(system_architecture: dict) -> dict:
    prompt = _json_guard(f"""
Explain the key architectural decisions.
Each explanation MUST include decision, rationale, risk, confidence.

System:
{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "explanations": [
    {{
      "decision": "",
      "rationale": "",
      "risk": "LOW|MEDIUM|HIGH",
      "confidence": 0.0
    }}
  ]
}}
""")

    data = _generate_json(prompt)

    explanations = []
    for e in data.get("explanations", []):
        try:
            confidence = float(e.get("confidence", 0.75))
        except Exception:
            confidence = 0.75

        explanations.append({
            "decision": e.get("decision", ""),
            "rationale": e.get("rationale", ""),
            "risk": e.get("risk", "MEDIUM"),
            "confidence": max(0.0, min(confidence, 1.0))
        })

    return {
        "explanations": explanations
    }
