from __future__ import annotations

from collections.abc import Iterable

from core.usig.schema import USIGraph


class USIGMerger:
    """Merge multiple USIG graphs into one canonical graph."""

    def merge(
        self,
        graphs: Iterable[USIGraph],
    ) -> USIGraph:
        graphs = list(graphs)

        if not graphs:
            raise ValueError(
                "At least one USIG graph is required."
            )

        primary = graphs[0]

        # Project information lives inside graph.project.
        merged = USIGraph(
            project_id=primary.project["id"],
            project_name=primary.project["name"],
            root=primary.project["root"],
            languages=[],
        )

        languages = set()

        for graph in graphs:
            languages.update(
                graph.project.get(
                    "languages",
                    [],
                )
            )

            # Nodes use deterministic IDs.
            # add_node() will keep one canonical node
            # when multiple graphs contain the same ID.
            for node in graph.nodes.values():
                merged.add_node(node)

            # Same principle applies to edges.
            for graph_edge in graph.edges.values():
                merged.add_edge(graph_edge)

        merged.project["languages"] = sorted(
            languages
        )

        return merged