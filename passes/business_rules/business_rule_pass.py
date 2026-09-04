from __future__ import annotations

from core.usig.factory import business_rule_node, edge
from core.usig.schema import USIGraph
from passes.base import AnalysisPass


class BusinessRulePass(AnalysisPass):
    """Extract business-rule intelligence from USIG function conditions."""

    @property
    def name(self) -> str:
        return "business_rules"

    def run(self, graph: USIGraph) -> USIGraph:
        function_nodes = [
            node
            for node in graph.nodes.values()
            if node.type == "Function"
        ]

        for function_node in function_nodes:
            conditions = function_node.attributes.get(
                "conditions",
                [],
            )

            for condition_data in conditions:
                expression = condition_data.get(
                    "expression",
                    "conditional expression",
                )

                start_line = condition_data.get(
                    "start_line",
                )

                end_line = condition_data.get(
                    "end_line",
                    start_line,
                )

                file_path = (
                    function_node.source.file_path
                    or "unknown"
                )

                rule_key = (
                    f"{function_node.qualified_name}."
                    f"{start_line}.rule"
                )

                title = self._title_from_condition(
                    expression
                )

                description = (
                    f"When `{expression}` is true, "
                    "this function follows a distinct "
                    "business or validation path."
                )

                rule = business_rule_node(
                    rule_key,
                    title,
                    description,
                    file_path,
                    start_line or 1,
                    end_line or start_line or 1,
                    0.68,
                    expression,
                )

                graph.add_node(rule)

                graph.add_edge(
                    edge(
                        function_node.id,
                        rule.id,
                        "IMPLEMENTS_RULE",
                        "business_rule_pass",
                        confidence=0.68,
                        evidence=expression,
                    )
                )

        return graph

    def _title_from_condition(
        self,
        condition: str,
    ) -> str:
        lowered = condition.lower()

        if "premium" in lowered:
            return "Premium Customer Rule"

        if "age" in lowered or "senior" in lowered:
            return "Age-Based Eligibility Rule"

        if "status" in lowered:
            return "Status Validation Rule"

        if (
            "total" in lowered
            or "amount" in lowered
            or "price" in lowered
        ):
            return "Amount-Based Calculation Rule"

        return "Conditional Business Rule"