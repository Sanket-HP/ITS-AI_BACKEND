import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# ==================================================
# Setup
# ==================================================

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-pro"
model = genai.GenerativeModel(MODEL_NAME)

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

{instruction}
"""

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
    return model.generate_content(prompt).text

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
    return model.generate_content(prompt).text

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
  "risk_level": "LOW | MEDIUM | HIGH"
}}
""")
    return model.generate_content(prompt).text

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
    return model.generate_content(prompt).text

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
    return model.generate_content(prompt).text
