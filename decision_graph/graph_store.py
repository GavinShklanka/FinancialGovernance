"""
Antigravity — Graph store (Stage 6): updated for new Node structure.
"""

import json
import os
from dataclasses import asdict

from decision_graph.decision_graph_builder import Node


GRAPH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "decision_graph"
)


class GraphStore:
    """Persist decision-graph nodes to the filesystem."""

    def __init__(self, graph_dir: str = GRAPH_DIR):
        self.graph_dir = graph_dir
        os.makedirs(self.graph_dir, exist_ok=True)

    def save_node(self, node: Node) -> None:
        """Write a single node as a JSON file keyed by its ID."""
        path = os.path.join(self.graph_dir, f"{node.node_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(node), f, indent=2)
        print(f"  → Graph node saved: {node.node_type} → {node.node_id}")
