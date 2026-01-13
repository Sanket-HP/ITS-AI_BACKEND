import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# ==================================================
# Setup
# ==================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_API_KEY)

# IMPORTANT:
# google-generativeai SDK DOES NOT support gemini-1.5-pro
MODEL_NAME = "gemini-1.0-pro"

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
- No trailing commas
- Output must start with '{{' and end with '}}'

{instruction}
"""

def _generate(prompt: str) -> str:
    """
    Centralized Gemini call.
    Keeps model creation local (important for server stability).
    """
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }
    )
    response = model.generate_content(prompt)
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
Design a system architecture from this intent:
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
Analyze failure modes for:
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
Optimize system for objective: {objective}

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
Explain decisions for:
{json.dumps(system_architecture, indent=2)}

JSON:
{{
  "explanations": []
}}
""")
    return _generate(prompt)
