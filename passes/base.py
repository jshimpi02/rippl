from __future__ import annotations

from abc import ABC, abstractmethod

from core.usig.schema import USIGraph


class AnalysisPass(ABC):
    """Base class for all Rippl analysis passes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable identifier for the analysis pass."""
        raise NotImplementedError

    @abstractmethod
    def run(self, graph: USIGraph) -> USIGraph:
        """Run the analysis pass against a USIG graph."""
        raise NotImplementedError