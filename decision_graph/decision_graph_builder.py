"""
Antigravity — Decision Graph upgrade (Stage 6).

Builds a full cycle graph with: signal → regime → portfolio → governance → human_approval.
Saves all nodes as a single consolidated decision_graph.json at project root.
"""

import json
import os
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from system_integrity.atomic_writer import atomic_write_json
from system_integrity.snapshot_validator import validate_json_structure
from system_integrity.recovery_manager import backup_snapshot


GRAPH_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "decision_graph.json"
)

# Legacy per-node dir (kept for backward compat)
GRAPH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "decision_graph"
)


@dataclass
class Node:
    """A single node in the decision graph."""
    node_id: str
    node_type: str
    description: str
    timestamp: str
    parent_id: Optional[str] = None
    metadata: dict = None  # type: ignore


class DecisionGraphBuilder:
    """Factory for decision-graph nodes."""

    @staticmethod
    def create_node(
        node_type: str,
        description: str,
        parent_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Node:
        return Node(
            node_id=str(uuid.uuid4()),
            node_type=node_type,
            description=description,
            timestamp=datetime.now(timezone.utc).isoformat(),
            parent_id=parent_id,
            metadata=metadata or {},
        )

    @staticmethod
    def build_cycle_graph(
        signal_score: float,
        regimes: list[str],
        portfolio_stance: str,
        governance_passed: bool,
    ) -> list[Node]:
        """Build the full 5-node reasoning chain for one pipeline cycle."""

        signal_node = DecisionGraphBuilder.create_node(
            node_type="signal_node",
            description=f"Signal scoring complete. Total weighted score: {signal_score:+.2f}",
            metadata={"total_score": signal_score},
        )

        regime_node = DecisionGraphBuilder.create_node(
            node_type="regime_node",
            description=f"Macro regime(s) detected: {', '.join(regimes)}",
            parent_id=signal_node.node_id,
            metadata={"regimes": regimes},
        )

        portfolio_node = DecisionGraphBuilder.create_node(
            node_type="portfolio_node",
            description=f"Three-engine portfolio built. Stance: {portfolio_stance.upper()}",
            parent_id=regime_node.node_id,
            metadata={"stance": portfolio_stance},
        )

        governance_node = DecisionGraphBuilder.create_node(
            node_type="governance_node",
            description=f"Governance check: {'PASSED' if governance_passed else 'FAILED — violations present'}",
            parent_id=portfolio_node.node_id,
            metadata={"passed": governance_passed},
        )

        human_node = DecisionGraphBuilder.create_node(
            node_type="human_approval_node",
            description="Awaiting human review. Claude briefing generated. Execution pending decision.",
            parent_id=governance_node.node_id,
            metadata={"claude_prompt": "app/outputs/claude_prompt.txt"},
        )

        return [signal_node, regime_node, portfolio_node, governance_node, human_node]


class GraphStore:
    """Persist decision-graph nodes to the filesystem."""

    def __init__(self, graph_dir: str = GRAPH_DIR):
        self.graph_dir = graph_dir
        os.makedirs(self.graph_dir, exist_ok=True)

    def save_node(self, node: Node) -> None:
        """Write a single node as a JSON file (legacy compat)."""
        path = os.path.join(self.graph_dir, f"{node.node_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(node), f, indent=2)

    def save_cycle_graph(self, nodes: list[Node]) -> None:
        """Save all cycle nodes as a single consolidated decision_graph.json."""
        payload = {
            "cycle_timestamp": datetime.now(timezone.utc).isoformat(),
            "node_count": len(nodes),
            "nodes": [asdict(n) for n in nodes],
        }
        backup_snapshot(GRAPH_PATH)
        validate_json_structure(payload, ["cycle_timestamp", "node_count", "nodes"])
        atomic_write_json(payload, GRAPH_PATH)
        print(f"  [Stage 6] Decision graph saved → {GRAPH_PATH}  ({len(nodes)} nodes)")
