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

# ✅ SAFE, AVAILABLE MODEL
MODEL_NAME = "models/gemini-pro-latest"

# ==================================================
# Helper: STRICT JSON GUARD
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


def _generate(prompt: str) -> str:
    """
    Centralized Gemini call with safety defaults
    """
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response or not response.text:
        raise RuntimeError("Empty response from Gemini")

    return response.text.strip()


# ==================================================
# 1. ANALYZE INTENT
# ==================================================

def analyze_intent(content: str) -> str:
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
    return _generate(prompt)


# ==================================================
# 2. GENERATE SYSTEM ARCHITECTURE
# ==================================================

def generate_system_architecture(intent_analysis: dict) -> str:
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
    return _generate(prompt)


# ==================================================
# 3. SIMULATE FAILURE
# ==================================================

def simulate_failure(system_architecture: dict) -> str:
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
    return _generate(prompt)


# ==================================================
# 4. OPTIMIZE SYSTEM
# ==================================================

def optimize_system(system_architecture: dict, objective: str) -> str:
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
    return _generate(prompt)


# ==================================================
# 5. EXPLAIN SYSTEM
# ==================================================

def explain_system(system_architecture: dict) -> str:
    prompt = _json_guard(f"""
Explain the architectural decisions for this system:

{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "explanations": []
}}
""")
    return _generate(prompt)
