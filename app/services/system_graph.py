from typing import Dict
from app.models.schemas import (
    SystemArchitecture,
    SystemGraph,
    GraphNode,
    GraphEdge
)


def build_system_graph(architecture: SystemArchitecture) -> SystemGraph:
    """
    Converts a SystemArchitecture into a graph representation
    suitable for visualization (D3 / React Flow / Mermaid).
    """

    nodes: Dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    # =========================
    # 1. MODULE NODES
    # =========================
    for module in architecture.modules:
        nodes[module.name] = GraphNode(
            id=module.name,
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
        for step in flow.steps:
            if "->" not in step:
                continue

            parts = [p.strip() for p in step.split("->")]

            for i in range(len(parts) - 1):
                source = parts[i]
                target = parts[i + 1]

                # Ensure phantom nodes are created if missing
                if source not in nodes:
                    nodes[source] = GraphNode(
                        id=source,
                        label=source,
                        type="external"
                    )

                if target not in nodes:
                    nodes[target] = GraphNode(
                        id=target,
                        label=target,
                        type="external"
                    )

                edges.append(
                    GraphEdge(
                        source=source,
                        target=target,
                        label=flow.flow_name,
                        edge_type="data_flow"
                    )
                )

    # =========================
    # 3. DECISION RULE OVERLAYS
    # =========================
    for idx, rule in enumerate(architecture.decision_rules):
        decision_node_id = f"decision_{idx + 1}"

        nodes[decision_node_id] = GraphNode(
            id=decision_node_id,
            label=f"Decision {idx + 1}",
            type="decision",
            metadata={
                "decision": rule.decision,
                "justification": rule.justification,
                "confidence": getattr(rule, "confidence", None),
                "risk_level": getattr(rule, "risk_level", None)
            }
        )

        # Attach decision to affected modules (best-effort)
        for module in architecture.modules:
            edges.append(
                GraphEdge(
                    source=decision_node_id,
                    target=module.name,
                    label="influences",
                    edge_type="decision"
                )
            )

    return SystemGraph(
        nodes=list(nodes.values()),
        edges=edges
    )
