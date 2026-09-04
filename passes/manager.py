from __future__ import annotations

from collections.abc import Iterable

from core.usig.schema import USIGraph
from passes.base import AnalysisPass


class PassManager:
    """Runs Rippl analysis passes in sequence."""

    def __init__(self, passes: Iterable[AnalysisPass] | None = None):
        self._passes = list(passes or [])

    @property
    def passes(self) -> tuple[AnalysisPass, ...]:
        return tuple(self._passes)

    def register(self, analysis_pass: AnalysisPass) -> None:
        self._passes.append(analysis_pass)

    def run(self, graph: USIGraph) -> USIGraph:
        current_graph = graph

        for analysis_pass in self._passes:
            current_graph = analysis_pass.run(current_graph)

        return current_graph