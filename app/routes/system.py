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

router = APIRouter()

# ==================================================
# Helper: Normalize System Architecture (Frontend Contract)
# ==================================================

def normalize_system_architecture(raw: dict) -> dict:
    # -------- data_flow --------
    normalized_data_flow = []

    for item in raw.get("data_flow", []):
        if isinstance(item, dict) and "flow_name" in item and "steps" in item:
            normalized_data_flow.append(item)
            continue

        if isinstance(item, dict):
            step = f"{item.get('from', '')} -> {item.get('to', '')}".strip()
            normalized_data_flow.append({
                "flow_name": "General Flow",
                "steps": [step]
            })
            continue

        if isinstance(item, str):
            normalized_data_flow.append({
                "flow_name": "General Flow",
                "steps": [item]
            })

    # -------- decision_rules --------
    normalized_decision_rules = []

    for rule in raw.get("decision_rules", []):
        if isinstance(rule, dict):
            normalized_decision_rules.append({
                "decision": rule.get("decision") or "Architectural decision",
                "justification": rule.get("justification", "Derived from system requirements"),
                "confidence": float(rule.get("confidence", 85)),
                "risk_level": rule.get("risk_level", "MEDIUM"),
            })
        elif isinstance(rule, str):
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
        if isinstance(fp, dict):
            normalized_points.append({
                "point": fp.get("point", "Unknown Component"),
                "description": fp.get("description", "Operational risk identified."),
                "impact": fp.get("impact", "Service degradation"),
                "mitigation": fp.get(
                    "mitigation",
                    "Implement redundancy, monitoring, automated failover."
                ),
                "affected_modules": fp.get("affected_modules", []),
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
    try:
        return analyze_intent(data.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Generate System Architecture
# ==================================================

@router.post(
    "/generate-system",
    response_model=SystemArchitecture,
    summary="Generate system architecture from intent analysis",
)
def generate_system(intent: IntentAnalysis):
    try:
        architecture = generate_system_architecture(intent.dict())
        return normalize_system_architecture(architecture)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Simulate Failure
# ==================================================

@router.post(
    "/simulate-failure",
    response_model=FailureSimulation,
    summary="Simulate failure scenarios for a system",
)
def simulate(system: SystemArchitecture):
    try:
        simulation = simulate_failure(system.dict())
        return normalize_failure_simulation(simulation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Optimize System
# ==================================================

@router.post(
    "/optimize-system",
    response_model=OptimizationResult,
    summary="Optimize system architecture based on objective",
)
def optimize(data: OptimizationInput):
    try:
        return optimize_system(
            data.system_architecture,
            data.objective
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================================================
# Explain System (Frontend-safe)
# ==================================================

@router.post(
    "/explain-system",
    response_model=SystemExplanation,
    summary="Explain why system decisions were made",
)
def explain(system: SystemArchitecture):
    try:
        parsed = explain_system(system.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    explanation_items = []

    for item in parsed.get("explanations", []):
        explanation_items.append(
            ExplanationItem(
                decision=item.get("decision", "Architectural decision"),
                justification=item.get("justification", ""),
                confidence=float(item.get("confidence", 85)),
                risk_level=item.get("risk_level", "MEDIUM"),
            )
        )

    return SystemExplanation(explanations=explanation_items)


# ==================================================
# System Graph
# ==================================================

@router.post(
    "/system-graph",
    response_model=SystemGraph,
    summary="Generate visual system graph",
)
def system_graph(system: SystemArchitecture):
    return build_system_graph(system)
