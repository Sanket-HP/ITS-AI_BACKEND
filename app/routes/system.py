from fastapi import APIRouter
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
    raw.setdefault("modules", [])
    raw.setdefault("data_flow", [])
    raw.setdefault("decision_rules", [])
    return raw


# ==================================================
# Helper: Normalize Failure Simulation (NEW SCHEMA)
# ==================================================

def normalize_failure_simulation(raw: dict) -> dict:
    normalized = []

    for fp in raw.get("failure_points", []):
        normalized.append({
            "point": fp.get("component", "Unknown Component"),
            "description": fp.get("failure", "Failure scenario identified."),
            "impact": fp.get("impact", "Operational degradation."),
            "severity": fp.get("severity", "MEDIUM"),
        })

    return {
        "failure_points": normalized,
        "overall_risk": raw.get("overall_risk", "MEDIUM"),
    }


# ==================================================
# Analyze Intent
# ==================================================

@router.post(
    "/analyze-intent",
    response_model=IntentAnalysis,
    summary="Analyze human intent into structured goals",
)
def analyze(data: IntentInput):
    return analyze_intent(data.content)


# ==================================================
# Generate System Architecture
# ==================================================

@router.post(
    "/generate-system",
    response_model=SystemArchitecture,
    summary="Generate system architecture from intent analysis",
)
def generate_system(intent: IntentAnalysis):
    architecture = generate_system_architecture(intent.dict())
    return normalize_system_architecture(architecture)


# ==================================================
# Simulate Failure
# ==================================================

@router.post(
    "/simulate-failure",
    response_model=FailureSimulation,
    summary="Simulate failure scenarios for a system",
)
def simulate(system: SystemArchitecture):
    simulation = simulate_failure(system.dict())
    return normalize_failure_simulation(simulation)


# ==================================================
# Optimize System
# ==================================================

@router.post(
    "/optimize-system",
    response_model=OptimizationResult,
    summary="Optimize system architecture based on objective",
)
def optimize(data: OptimizationInput):
    return optimize_system(
        data.system_architecture,
        data.objective
    )


# ==================================================
# Explain System (UPDATED EXPLAINABILITY)
# ==================================================

@router.post(
    "/explain-system",
    response_model=SystemExplanation,
    summary="Explain why system decisions were made",
)
def explain(system: SystemArchitecture):
    parsed = explain_system(system.dict())

    explanation_items = []

    for item in parsed.get("explanations", []):
        explanation_items.append(
            ExplanationItem(
                decision=item.get("decision", "Architectural decision"),
                justification=item.get("rationale", ""),
                confidence=float(item.get("confidence", 0.85) * 100),
                risk_level=item.get("risk", "MEDIUM"),
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
