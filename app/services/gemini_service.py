import os
import json
from dotenv import load_dotenv
from google import genai

# ==================================================
# Setup
# ==================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment")

client = genai.Client(api_key=GEMINI_API_KEY)

# Use latest stable Gemini Pro model
MODEL_NAME = "models/gemini-pro-latest"


# ==================================================
# Helper: STRICT JSON GUARD
# ==================================================

def _json_guard(instruction: str) -> str:
    """
    Enforces strict machine-parseable JSON output.
    This is CRITICAL for FastAPI + Pydantic reliability.
    """
    return f"""
IMPORTANT RULES (ABSOLUTE – NO EXCEPTIONS):
- Respond with ONLY valid JSON
- Do NOT include markdown
- Do NOT include comments
- Do NOT include explanations outside JSON
- Do NOT include trailing commas
- JSON must start with '{{' and end with '}}'
- Every field must match the schema exactly
- Arrays must be valid JSON arrays

{instruction}
""".strip()


# ==================================================
# 1. ANALYZE INTENT
# ==================================================

def analyze_intent(content: str) -> str:
    prompt = _json_guard(f"""
You are an expert AI system architect.

Decompose the following intent into structured system requirements.

Return:
- goals
- constraints
- actors
- success_metrics

Intent:
{content}

JSON schema:
{{
  "goals": ["..."],
  "constraints": ["..."],
  "actors": ["..."],
  "success_metrics": ["..."]
}}
""")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# ==================================================
# 2. GENERATE SYSTEM ARCHITECTURE
# ==================================================

def generate_system_architecture(intent_analysis: dict) -> str:
    prompt = _json_guard(f"""
You are a senior distributed systems architect.

Design a production-grade, scalable, fault-tolerant system.

For EACH decision rule include:
- decision
- justification
- confidence (0–100)
- risk_level (LOW | MEDIUM | HIGH)

Intent analysis:
{json.dumps(intent_analysis, indent=2)}

JSON schema:
{{
  "modules": [
    {{
      "name": "",
      "responsibility": "",
      "inputs": [],
      "outputs": []
    }}
  ],
  "data_flow": [
    {{
      "flow_name": "",
      "steps": []
    }}
  ],
  "decision_rules": [
    {{
      "decision": "",
      "justification": "",
      "confidence": 85,
      "risk_level": "MEDIUM"
    }}
  ]
}}
""")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# ==================================================
# 3. SIMULATE FAILURE
# ==================================================

def simulate_failure(system_architecture: dict) -> str:
    prompt = _json_guard(f"""
You are a senior reliability and risk engineer.

Perform failure-mode, stress, and resilience analysis.

For EACH failure point include:
- point
- description
- impact
- affected_modules
- mitigation

System architecture:
{json.dumps(system_architecture, indent=2)}

JSON schema:
{{
  "best_case": "",
  "worst_case": "",
  "failure_points": [
    {{
      "point": "",
      "description": "",
      "impact": "",
      "affected_modules": [],
      "mitigation": ""
    }}
  ],
  "risk_level": "LOW | MEDIUM | HIGH"
}}
""")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# ==================================================
# 4. OPTIMIZE SYSTEM
# ==================================================

def optimize_system(system_architecture: dict, objective: str) -> str:
    prompt = _json_guard(f"""
You are a system optimization AI.

Primary optimization objective: {objective}

Redesign the system while preserving correctness,
security, and observability.

For EACH optimized decision include:
- decision
- justification
- confidence
- risk_level

System architecture:
{json.dumps(system_architecture, indent=2)}

JSON schema:
{{
  "optimized_architecture": {{
    "modules": [
      {{
        "name": "",
        "responsibility": "",
        "inputs": [],
        "outputs": []
      }}
    ],
    "data_flow": [
      {{
        "flow_name": "",
        "steps": []
      }}
    ],
    "decision_rules": [
      {{
        "decision": "",
        "justification": "",
        "confidence": 90,
        "risk_level": "LOW | MEDIUM | HIGH"
      }}
    ]
  }},
  "tradeoffs": {{
    "cost": "",
    "speed": "",
    "fairness": ""
  }}
}}
""")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()


# ==================================================
# 5. EXPLAIN SYSTEM (STRUCTURED XAI)
# ==================================================

def explain_system(system_architecture: dict) -> str:
    prompt = _json_guard(f"""
You are an Explainable AI (XAI) system.

Explain WHY each architectural decision was made.

For EACH explanation include:
- decision
- justification
- confidence (0–100)
- risk_level (LOW | MEDIUM | HIGH)

System architecture:
{json.dumps(system_architecture, indent=2)}

JSON schema:
{{
  "explanations": [
    {{
      "decision": "",
      "justification": "",
      "confidence": 88,
      "risk_level": "MEDIUM"
    }}
  ]
}}
""")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()
