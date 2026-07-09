from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Tuple


RISK_EDGE_WEIGHTS = {
    "CALLS": 0.85,
    "IMPLEMENTS_RULE": 0.90,
    "HAS_RISK": 0.95,
    "TESTED_BY": 0.35,
    "DECLARES": 0.40,
    "CONTAINS": 0.25,
    "WRITES": 0.95,
    "READS": 0.70,
    "CALLS_API": 0.80,
    "EXPOSES_API": 0.75,
}

NODE_CRITICALITY = {
    "RiskFinding": 1.00,
    "BusinessRule": 0.90,
    "DatabaseTable": 0.95,
    "APIEndpoint": 0.85,
    "Method": 0.75,
    "Function": 0.75,
    "Class": 0.55,
    "File": 0.35,
    "Repository": 0.20,
    "TestCase": 0.30,
}


class RipplePropagationEngine:
    def __init__(self, usig: Dict[str, Any], decay: float = 0.72, max_depth: int = 4):
        self.usig = usig
        self.decay = decay
        self.max_depth = max_depth
        self.nodes = {node["id"]: node for node in usig.get("nodes", [])}
        self.outgoing = defaultdict(list)
        self.incoming = defaultdict(list)
        for edge in usig.get("edges", []):
            self.outgoing[edge["source"]].append(edge)
            self.incoming[edge["target"]].append(edge)

    def analyze(self, changed_node: str) -> Dict[str, Any]:
        if changed_node not in self.nodes:
            raise ValueError(f"Node not found: {changed_node}")

        affected: Dict[str, Dict[str, Any]] = {}
        queue = deque([(changed_node, 1.0, 0, [])])
        visited_best = {changed_node: 1.0}

        while queue:
            current, strength, depth, path = queue.popleft()
            if depth >= self.max_depth:
                continue

            candidate_edges = self.outgoing[current] + self.incoming[current]
            for e in candidate_edges:
                nxt = e["target"] if e["source"] == current else e["source"]
                if nxt == changed_node:
                    continue
                weight = RISK_EDGE_WEIGHTS.get(e["type"], 0.50)
                next_strength = strength * weight * self.decay
                if next_strength < 0.08:
                    continue
                if next_strength <= visited_best.get(nxt, 0):
                    continue
                visited_best[nxt] = next_strength
                node = self.nodes[nxt]
                criticality = NODE_CRITICALITY.get(node.get("type"), 0.5)
                impact = next_strength * criticality
                new_path = path + [e["id"]]
                affected[nxt] = {
                    "node_id": nxt,
                    "type": node.get("type"),
                    "name": node.get("name"),
                    "propagation_strength": round(next_strength, 4),
                    "criticality": criticality,
                    "impact_score": round(impact, 4),
                    "depth": depth + 1,
                    "via_edge_type": e["type"],
                    "path_edges": new_path,
                }
                queue.append((nxt, next_strength, depth + 1, new_path))

        ranked = sorted(affected.values(), key=lambda x: x["impact_score"], reverse=True)
        ripple_score = min(1.0, sum(x["impact_score"] for x in ranked[:10]) / 3.0)
        risk_level = "High" if ripple_score >= 0.70 else "Medium" if ripple_score >= 0.35 else "Low"
        recommended_tests = self._recommend_tests(ranked)

        return {
            "changed_node": changed_node,
            "changed_node_name": self.nodes[changed_node].get("name"),
            "ripple_score": round(ripple_score, 4),
            "risk_level": risk_level,
            "affected_count": len(ranked),
            "affected_nodes": ranked,
            "recommended_tests": recommended_tests,
            "explanation": self._explain(risk_level, ripple_score, ranked),
        }

    def _recommend_tests(self, affected: List[Dict[str, Any]]) -> List[str]:
        recs = []
        types = {item["type"] for item in affected[:10]}
        names = " ".join(item["name"].lower() for item in affected[:10] if item.get("name"))
        if "BusinessRule" in types:
            recs.append("Add regression tests for each affected business rule.")
        if "RiskFinding" in types:
            recs.append("Add targeted tests around high-risk logic before merging.")
        if any(token in names for token in ["tax", "discount", "invoice", "payment", "financial"]):
            recs.append("Add financial boundary tests for rounding, zero values, and large amounts.")
        recs.append("Run tests covering directly called and calling functions.")
        return recs

    def _explain(self, risk_level: str, score: float, affected: List[Dict[str, Any]]) -> str:
        top = affected[:3]
        if not top:
            return "No significant ripple detected from this node."
        names = ", ".join(f"{x['name']} ({x['type']})" for x in top)
        return f"{risk_level} ripple risk because the change propagates to {len(affected)} nodes. Highest-impact affected nodes: {names}."


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run Rippl Ripple Propagation Engine over a USIG JSON file.")
    parser.add_argument("usig", help="Path to usig.json")
    parser.add_argument("changed_node", help="Changed node ID")
    parser.add_argument("--out", default="ripple_report.json", help="Output report path")
    args = parser.parse_args()

    usig = json.loads(Path(args.usig).read_text(encoding="utf-8"))
    report = RipplePropagationEngine(usig).analyze(args.changed_node)
    Path(args.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}: {report['risk_level']} risk, score={report['ripple_score']}")


if __name__ == "__main__":
    main()
