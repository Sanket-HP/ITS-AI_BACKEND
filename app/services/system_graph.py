from typing import Dict
import re
from app.models.schemas import (
    SystemArchitecture,
    SystemGraph,
    GraphNode,
    GraphEdge
)


def _safe_id(name: str) -> str:
    """
    Generates a graph-safe ID (Mermaid / D3 safe).
    """
    if not name:
        return "unknown"
    return "N_" + re.sub(r"[^a-zA-Z0-9_]", "_", name)


def build_system_graph(architecture: SystemArchitecture) -> SystemGraph:
    """
    Converts a SystemArchitecture into a graph representation
    suitable for visualization (Mermaid / D3 / React Flow).
    """

    nodes: Dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    # =========================
    # 1. MODULE NODES
    # =========================
    for module in architecture.modules:
        node_id = _safe_id(module.name)

        nodes[node_id] = GraphNode(
            id=node_id,
            label=module.name,
            type="module",
            metadata={
                "responsibility": module.responsibility,
                "inputs": module.inputs or [],
                "outputs": module.outputs or []
            }
        )

    # =========================
    # 2. DATA FLOW EDGES
    # =========================
    for flow in architecture.data_flow:
        for step in getattr(flow, "steps", []):
            if "->" not in step:
                continue

            parts = [p.strip() for p in step.split("->")]

            for i in range(len(parts) - 1):
                source_label = parts[i]
                target_label = parts[i + 1]

                source_id = _safe_id(source_label)
                target_id = _safe_id(target_label)

                # Create external nodes if missing
                if source_id not in nodes:
                    nodes[source_id] = GraphNode(
                        id=source_id,
                        label=source_label,
                        type="external"
                    )

                if target_id not in nodes:
                    nodes[target_id] = GraphNode(
                        id=target_id,
                        label=target_label,
                        type="external"
                    )

                edges.append(
                    GraphEdge(
                        source=source_id,
                        target=target_id,
                        label=getattr(flow, "flow_name", ""),
                        edge_type="data_flow"
                    )
                )

    # =========================
    # 3. DECISION RULE OVERLAYS (CLEANED)
    # =========================
    for idx, rule in enumerate(architecture.decision_rules):
        decision_id = f"DECISION_{idx + 1}"

        nodes[decision_id] = GraphNode(
            id=decision_id,
            label=f"Decision {idx + 1}",
            type="decision",
            metadata={
                "decision": getattr(rule, "decision", ""),
                "rationale": getattr(rule, "rationale", ""),
                "confidence": getattr(rule, "confidence", None),
                "risk": getattr(rule, "risk", None),
            }
        )

        # Attach decision to system (single anchor edge)
        for module in architecture.modules[:1]:
            edges.append(
                GraphEdge(
                    source=decision_id,
                    target=_safe_id(module.name),
                    label="influences",
                    edge_type="decision"
                )
            )

    return SystemGraph(
        nodes=list(nodes.values()),
        edges=edges
    )
