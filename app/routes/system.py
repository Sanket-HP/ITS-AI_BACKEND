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
# Helper: Normalize System Architecture (CRITICAL FIX)
# ==================================================

def normalize_system_architecture(raw: dict) -> dict:
    # -------------------------
    # Normalize data_flow
    # -------------------------
    normalized_data_flow = []

    for item in raw.get("data_flow", []):
        # Case 1: already valid
        if isinstance(item, dict) and "flow_name" in item and "steps" in item:
            normalized_data_flow.append(item)
            continue

        # Case 2: from/to/data format
        if isinstance(item, dict) and "from" in item and "to" in item:
            step = f"{item['from']} -> {item['to']}"
            normalized_data_flow.append({
                "flow_name": item.get("data", "Data Flow"),
                "steps": [step]
            })
            continue

        # Case 3: string fallback
        if isinstance(item, str):
            normalized_data_flow.append({
                "flow_name": "Data Flow",
                "steps": [item]
            })

    # -------------------------
    # Normalize decision_rules
    # -------------------------
    normalized_decision_rules = []

    for rule in raw.get("decision_rules", []):
        # Case 1: already valid
        if isinstance(rule, dict) and "decision" in rule:
            normalized_decision_rules.append(rule)
            continue

        # Case 2: rule_name / condition / action
        if isinstance(rule, dict):
            normalized_decision_rules.append({
                "decision": rule.get("rule_name")
                or rule.get("description")
                or "Architectural decision",
                "justification": (
                    f"Condition: {rule.get('condition', '')}. "
                    f"Action: {rule.get('action', '')}"
                ).strip(),
                "confidence": 85,
                "risk_level": "MEDIUM",
            })

    raw["modules"] = raw.get("modules", [])
    raw["data_flow"] = normalized_data_flow
    raw["decision_rules"] = normalized_decision_rules

    return raw


# ==================================================
# Helper: Normalize Failure Simulation
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

@router.post("/analyze-intent", response_model=IntentAnalysis)
def analyze(data: IntentInput):
    return analyze_intent(data.content)


# ==================================================
# Generate System Architecture
# ==================================================

@router.post("/generate-system", response_model=SystemArchitecture)
def generate_system(intent: IntentAnalysis):
    architecture = generate_system_architecture(intent.dict())
    return normalize_system_architecture(architecture)


# ==================================================
# Simulate Failure
# ==================================================

@router.post("/simulate-failure", response_model=FailureSimulation)
def simulate(system: SystemArchitecture):
    simulation = simulate_failure(system.dict())
    return normalize_failure_simulation(simulation)


# ==================================================
# Optimize System
# ==================================================

@router.post("/optimize-system", response_model=OptimizationResult)
def optimize(data: OptimizationInput):
    return optimize_system(
        data.system_architecture,
        data.objective
    )


# ==================================================
# Explain System
# ==================================================

@router.post("/explain-system", response_model=SystemExplanation)
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

@router.post("/system-graph", response_model=SystemGraph)
def system_graph(system: SystemArchitecture):
    return build_system_graph(system)
