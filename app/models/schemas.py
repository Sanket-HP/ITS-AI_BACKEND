from pydantic import BaseModel, Field
from typing import List, Dict, Optional


# =========================
# 1. INPUT SCHEMAS
# =========================

class IntentInput(BaseModel):
    content: str = Field(
        ...,
        example="Design a flood disaster response system for a coastal city"
    )


class OptimizationInput(BaseModel):
    objective: str = Field(..., example="resilience")
    system_architecture: Dict


# =========================
# 2. INTENT ANALYSIS OUTPUT
# =========================

class IntentAnalysis(BaseModel):
    goals: List[str]
    constraints: List[str]
    actors: List[str]
    success_metrics: List[str]


# =========================
# 3. SYSTEM ARCHITECTURE
# =========================

class SystemModule(BaseModel):
    name: str
    responsibility: str
    inputs: List[str] = []
    outputs: List[str] = []


class DataFlow(BaseModel):
    flow_name: str
    steps: List[str]


class DecisionRule(BaseModel):
    decision: str
    justification: str

    # 🔥 Confidence + Risk for frontend UI
    confidence: float = Field(
        default=85.0,
        ge=0,
        le=100,
        example=92.5
    )
    risk_level: str = Field(
        default="MEDIUM",
        example="LOW"  # LOW | MEDIUM | HIGH
    )


class SystemArchitecture(BaseModel):
    modules: List[SystemModule]
    data_flow: List[DataFlow]
    decision_rules: List[DecisionRule]


# =========================
# 4. FAILURE SIMULATION
# =========================

class FailurePoint(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    point: Optional[str] = None
    impact: Optional[str] = None
    description: str
    mitigation: Optional[str] = None
    affected_modules: Optional[List[str]] = None

    class Config:
        extra = "allow"  # allows flexible AI output


class FailureSimulation(BaseModel):
    best_case: str
    worst_case: str
    failure_points: List[FailurePoint]
    risk_level: str


# =========================
# 5. OPTIMIZATION OUTPUT
# =========================

class OptimizationResult(BaseModel):
    optimized_architecture: SystemArchitecture
    tradeoffs: Dict[str, str]


# =========================
# 6. EXPLANATION (STRUCTURED)
# =========================

class ExplanationItem(BaseModel):
    decision: str
    justification: str
    confidence: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., example="LOW")


class SystemExplanation(BaseModel):
    explanations: List[ExplanationItem]


# =========================
# 7. VISUAL GRAPH SUPPORT
# =========================

class GraphNode(BaseModel):
    id: str
    label: str
    type: str = "module"


class GraphEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None


class SystemGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


# =========================
# 8. FULL EXPORT REPORT
# =========================

class FullSystemReport(BaseModel):
    intent: IntentAnalysis
    architecture: SystemArchitecture
    graph: SystemGraph
    simulation: FailureSimulation
    optimization: OptimizationResult
    explanation: SystemExplanation
