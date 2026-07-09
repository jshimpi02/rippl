from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from .schema import Provenance, SourceLocation, USIGEdge, USIGNode


def slug(value: str) -> str:
    value = value.strip().replace("\\", "/")
    value = re.sub(r"[^A-Za-z0-9_./:-]+", "_", value)
    return value.strip("_")


def edge_id(source: str, target: str, edge_type: str) -> str:
    return f"edge:{source}->{target}:{edge_type}"


def repository_node(name: str, root: str) -> USIGNode:
    return USIGNode(
        id=f"repository:{slug(name)}",
        type="Repository",
        name=name,
        qualified_name=name,
        source=SourceLocation(file_path=root),
        provenance=Provenance(generated_by="repository_scanner", confidence=1.0),
    )


def file_node(relative_path: str, language: str) -> USIGNode:
    return USIGNode(
        id=f"file:{slug(relative_path)}",
        type="File",
        name=Path(relative_path).name,
        qualified_name=relative_path,
        language=language,
        source=SourceLocation(file_path=relative_path),
        provenance=Provenance(generated_by="repository_scanner", confidence=1.0),
    )


def function_node(file_path: str, function_name: str, start_line: int, end_line: int, attributes: Optional[dict] = None, metrics: Optional[dict] = None) -> USIGNode:
    qname = f"{file_path}.{function_name}"
    return USIGNode(
        id=f"function:{slug(qname)}",
        type="Function",
        name=function_name,
        qualified_name=qname,
        language="Python",
        source=SourceLocation(file_path=file_path, start_line=start_line, end_line=end_line),
        attributes=attributes or {},
        metrics=metrics or {},
        provenance=Provenance(generated_by="python_ast_parser", confidence=1.0),
    )


def class_node(file_path: str, class_name: str, start_line: int, end_line: int) -> USIGNode:
    qname = f"{file_path}.{class_name}"
    return USIGNode(
        id=f"class:{slug(qname)}",
        type="Class",
        name=class_name,
        qualified_name=qname,
        language="Python",
        source=SourceLocation(file_path=file_path, start_line=start_line, end_line=end_line),
        provenance=Provenance(generated_by="python_ast_parser", confidence=1.0),
    )


def business_rule_node(rule_slug: str, title: str, description: str, file_path: str, start_line: int, end_line: int, confidence: float, evidence: str) -> USIGNode:
    return USIGNode(
        id=f"rule:{slug(rule_slug)}",
        type="BusinessRule",
        name=title,
        qualified_name=f"business.{slug(rule_slug)}",
        language=None,
        source=SourceLocation(file_path=file_path, start_line=start_line, end_line=end_line),
        attributes={"description": description, "category": "InferredRule", "criticality": "Medium"},
        metrics={"confidence": confidence},
        provenance=Provenance(generated_by="heuristic_business_rule_extractor", confidence=confidence, evidence=evidence),
    )


def risk_node(risk_slug: str, title: str, description: str, recommendation: str, file_path: str, start_line: int, end_line: int, score: float, evidence: str) -> USIGNode:
    severity = "High" if score >= 0.75 else "Medium" if score >= 0.45 else "Low"
    return USIGNode(
        id=f"risk:{slug(risk_slug)}",
        type="RiskFinding",
        name=title,
        qualified_name=f"risk.{slug(risk_slug)}",
        language=None,
        source=SourceLocation(file_path=file_path, start_line=start_line, end_line=end_line),
        attributes={"severity": severity, "description": description, "recommendation": recommendation},
        metrics={"risk_score": score},
        provenance=Provenance(generated_by="risk_pass", confidence=0.85, evidence=evidence),
    )


def edge(source: str, target: str, edge_type: str, generated_by: str, confidence: float = 1.0, evidence: Optional[str] = None, attributes: Optional[dict] = None) -> USIGEdge:
    return USIGEdge(
        id=edge_id(source, target, edge_type),
        source=source,
        target=target,
        type=edge_type,
        attributes=attributes or {},
        provenance=Provenance(generated_by=generated_by, confidence=confidence, evidence=evidence),
    )
