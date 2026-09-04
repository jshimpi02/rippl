from __future__ import annotations

from core.usig.factory import edge, risk_node
from core.usig.schema import USIGraph
from passes.base import AnalysisPass


class RiskPass(AnalysisPass):
    """Detect risk signals from an existing USIG graph."""

    @property
    def name(self) -> str:
        return "risk"

    def run(self, graph: USIGraph) -> USIGraph:
        function_nodes = [
            node
            for node in graph.nodes.values()
            if node.type == "Function"
        ]

        for function_node in function_nodes:
            self._detect_complexity_risk(
                graph,
                function_node,
            )

            self._detect_financial_risk(
                graph,
                function_node,
            )

        return graph

    def _detect_complexity_risk(
        self,
        graph: USIGraph,
        function_node,
    ) -> None:
        complexity = function_node.metrics.get(
            "cyclomatic_complexity",
            1,
        )

        if complexity < 6:
            return

        file_path = (
            function_node.source.file_path
            or "unknown"
        )

        risk = risk_node(
            f"{file_path}.{function_node.name.split('.')[-1]}.complexity",
            "High Branching Complexity",
            (
                "This function contains several decision "
                "paths, increasing regression risk."
            ),
            (
                "Add boundary and branch-coverage tests "
                "before modifying this function."
            ),
            file_path,
            function_node.source.start_line or 1,
            function_node.source.end_line
            or function_node.source.start_line
            or 1,
            min(
                0.95,
                0.45 + complexity / 20,
            ),
            f"cyclomatic_complexity={complexity}",
        )

        graph.add_node(risk)

        graph.add_edge(
            edge(
                function_node.id,
                risk.id,
                "HAS_RISK",
                "risk_pass",
                confidence=0.85,
            )
        )

    def _detect_financial_risk(
        self,
        graph: USIGraph,
        function_node,
    ) -> None:
        financial_tokens = {
            "price",
            "amount",
            "total",
            "tax",
            "discount",
            "payment",
        }

        identifiers = {
            identifier.lower()
            for identifier in function_node.attributes.get(
                "identifiers",
                [],
            )
        }

        matched_tokens = sorted(
            identifiers & financial_tokens
        )

        if not matched_tokens:
            return

        file_path = (
            function_node.source.file_path
            or "unknown"
        )

        function_name = function_node.name.split(".")[-1]

        risk = risk_node(
            f"{file_path}.{function_name}.financial_logic",
            "Financial Logic Risk",
            (
                "This function appears to handle financial "
                "calculations or payment-related decisions."
            ),
            (
                "Add regression tests for rounding, "
                "boundary values, and invalid inputs."
            ),
            file_path,
            function_node.source.start_line or 1,
            function_node.source.end_line
            or function_node.source.start_line
            or 1,
            0.72,
            (
                "financial identifiers detected: "
                + ", ".join(matched_tokens)
            ),
        )

        graph.add_node(risk)

        graph.add_edge(
            edge(
                function_node.id,
                risk.id,
                "HAS_RISK",
                "risk_pass",
                confidence=0.8,
                evidence=", ".join(matched_tokens),
            )
        )