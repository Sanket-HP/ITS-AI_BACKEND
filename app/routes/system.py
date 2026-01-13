from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    IntentInput,
    IntentAnalysis,
    SystemArchitecture,
    FailureSimulation,
    OptimizationInput,
    OptimizationResult,
    SystemExplanation,
    ExplanationItem,
    SystemGraph,
)
from app.services.gemini_service import (
    analyze_intent,
    generate_system_architecture,
    simulate_failure,
    optimize_system,
    explain_system,
)
from app.services.system_graph import build_system_graph

import json
import re

router = APIRouter()

# ==================================================
# Helper: Normalize System Architecture
# ==================================================
def normalize_system_architecture(raw: dict) -> dict:
    # -------- Normalize data_flow --------
    normalized_data_flow = []

    for item in raw.get("data_flow", []):
        if isinstance(item, dict) and "flow_name" in item and "steps" in item:
            normalized_data_flow.append(item)
            continue

        if isinstance(item, dict):
            step = f"{item.get('from', '')} -> {item.get('to', '')}"
            normalized_data_flow.append({
                "flow_name": "General Flow",
                "steps": [step.strip()]
            })
            continue

        if isinstance(item, str):
            normalized_data_flow.append({
                "flow_name": "General Flow",
                "steps": [item]
            })

    # -------- Normalize decision_rules --------
    normalized_decision_rules = []

    for rule in raw.get("decision_rules", []):
        if isinstance(rule, dict) and "decision" in rule and "justification" in rule:
            normalized_decision_rules.append({
                "decision": rule["decision"],
                "justification": rule["justification"],
                "confidence": rule.get("confidence", 85.0),
                "risk_level": rule.get("risk_level", "MEDIUM"),
            })
            continue

        if isinstance(rule, dict):
            normalized_decision_rules.append({
                "decision": f"IF {rule.get('condition', '')} THEN {rule.get('action', '')}",
                "justification": "Derived from system requirements",
                "confidence": 80.0,
                "risk_level": "MEDIUM",
            })
            continue

        if isinstance(rule, str):
            normalized_decision_rules.append({
                "decision": rule,
                "justification": "Derived from system requirements",
                "confidence": 75.0,
                "risk_level": "MEDIUM",
            })

    raw["data_flow"] = normalized_data_flow
    raw["decision_rules"] = normalized_decision_rules

    return raw


# ==================================================
# Helper: Normalize Failure Simulation
# ==================================================
def normalize_failure_simulation(raw: dict) -> dict:
    normalized_points = []

    for fp in raw.get("failure_points", []):
        normalized_points.append({
            "point": fp.get("point", "Unknown Component"),
            "description": fp.get("description", "Operational risk identified."),
            "mitigation": fp.get(
                "mitigation",
                "Implement redundancy, monitoring, automated failover, and periodic resilience testing."
            ),
            "impact": fp.get("impact"),
            "affected_modules": fp.get("affected_modules"),
        })

    raw["failure_points"] = normalized_points
    raw.setdefault("best_case", "System remains operational with graceful degradation.")
    raw.setdefault("worst_case", "Cascading failures degrade system availability.")
    raw.setdefault("risk_level", "HIGH")

    return raw


# ==================================================
# Analyze Intent
# ==================================================
@router.post(
    "/analyze-intent",
    response_model=IntentAnalysis,
    summary="Analyze human intent into structured goals",
)
def analyze(data: IntentInput):
    raw = analyze_intent(data.content)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group())

    raise HTTPException(status_code=500, detail="Failed to parse intent analysis output")


# ==================================================
# Generate System Architecture
# ==================================================
@router.post(
    "/generate-system",
    response_model=SystemArchitecture,
    summary="Generate system architecture from intent analysis",
)
def generate_system(intent: IntentAnalysis):
    raw = generate_system_architecture(intent.dict())

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise HTTPException(status_code=500, detail="Failed to parse system architecture output")
        parsed = json.loads(match.group())

    return normalize_system_architecture(parsed)


# ==================================================
# Simulate Failure
# ==================================================
@router.post(
    "/simulate-failure",
    response_model=FailureSimulation,
    summary="Simulate failure scenarios for a system",
)
def simulate(system: SystemArchitecture):
    raw = simulate_failure(system.dict())

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise HTTPException(status_code=500, detail="Failed to parse failure simulation output")
        parsed = json.loads(match.group())

    return normalize_failure_simulation(parsed)


# ==================================================
# Optimize System
# ==================================================
@router.post(
    "/optimize-system",
    response_model=OptimizationResult,
    summary="Optimize system architecture based on objective",
)
def optimize(data: OptimizationInput):
    raw = optimize_system(data.system_architecture, data.objective)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group())

    raise HTTPException(status_code=500, detail="Failed to parse optimization output")


# ==================================================
# Explain System (STRUCTURED + SAFE)
# ==================================================
@router.post(
    "/explain-system",
    response_model=SystemExplanation,
    summary="Explain why system decisions were made",
)
def explain(system: SystemArchitecture):
    raw = explain_system(system.dict())

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise HTTPException(status_code=500, detail="Failed to parse explanation output")
        parsed = json.loads(match.group())

    explanation_items = []

    for item in parsed.get("explanations", []):
        if isinstance(item, dict):
            explanation_items.append(
                ExplanationItem(
                    decision=item.get("decision", "Architectural decision"),
                    justification=item.get("justification") or item.get("reasoning", ""),
                    confidence=float(item.get("confidence", 85)),
                    risk_level=item.get("risk_level", "MEDIUM"),
                )
            )

    return SystemExplanation(explanations=explanation_items)


# ==================================================
# System Graph (NEW)
# ==================================================
@router.post(
    "/system-graph",
    response_model=SystemGraph,
    summary="Generate visual system graph",
)
def system_graph(system: SystemArchitecture):
    return build_system_graph(system)
