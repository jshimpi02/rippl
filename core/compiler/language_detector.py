from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable


@dataclass(frozen=True)
class LanguageDetectionResult:
    counts: Dict[str, int]

    @property
    def total_files(self) -> int:
        return sum(self.counts.values())

    def detected_languages(self) -> list[str]:
        return [
            language
            for language, count in self.counts.items()
            if count > 0
        ]


class LanguageDetector:
    EXTENSION_MAP = {
        ".py": "Python",
        ".java": "Java",
        ".cs": "C#",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
    }

    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "dist",
        "build",
    }

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()

    def detect(self) -> LanguageDetectionResult:
        counts: Counter[str] = Counter()

        for path in self._iter_source_files():
            language = self.EXTENSION_MAP.get(
                path.suffix.lower()
            )

            if language:
                counts[language] += 1

        return LanguageDetectionResult(
            counts=dict(counts)
        )

    def _iter_source_files(self) -> Iterable[Path]:
        for path in self.repo_root.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in self.IGNORED_DIRECTORIES
                for part in path.parts
            ):
                continue

            if path.suffix.lower() in self.EXTENSION_MAP:
                yield path