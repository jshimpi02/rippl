from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Provenance:
    generated_by: str
    confidence: float = 1.0
    evidence: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class SourceLocation:
    file_path: Optional[str] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class USIGNode:
    id: str
    type: str
    name: str
    qualified_name: str
    language: Optional[str] = None
    source: SourceLocation = field(default_factory=SourceLocation)
    attributes: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    provenance: Provenance = field(default_factory=lambda: Provenance(generated_by="unknown"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "language": self.language,
            "source": self.source.to_dict(),
            "attributes": self.attributes,
            "metrics": self.metrics,
            "provenance": self.provenance.to_dict(),
        }


@dataclass
class USIGEdge:
    id: str
    source: str
    target: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    provenance: Provenance = field(default_factory=lambda: Provenance(generated_by="unknown"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "attributes": self.attributes,
            "provenance": self.provenance.to_dict(),
        }


class USIGraph:
    def __init__(self, project_id: str, project_name: str, root: str, languages: Optional[List[str]] = None):
        self.usig_version = "1.0"
        self.project = {
            "id": project_id,
            "name": project_name,
            "root": root,
            "languages": languages or [],
        }
        self.nodes: Dict[str, USIGNode] = {}
        self.edges: Dict[str, USIGEdge] = {}
        self.metadata = {
            "created_by": "rippl-usigc",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": "local_repository",
        }

    def add_node(self, node: USIGNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: USIGEdge) -> None:
        if edge.source not in self.nodes or edge.target not in self.nodes:
            # Store only valid edges in v1 to avoid dangling references.
            return
        self.edges[edge.id] = edge

    def to_dict(self) -> Dict[str, Any]:
        return {
            "usig_version": self.usig_version,
            "project": self.project,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges.values()],
            "metadata": self.metadata,
        }
