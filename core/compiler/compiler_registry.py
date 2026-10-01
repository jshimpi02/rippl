from __future__ import annotations

from typing import Dict, Type

from core.compiler.java_compiler import JavaUSIGCompiler
from core.compiler.python_compiler import PythonUSIGCompiler
from core.compiler.typescript_compiler import TypeScriptUSIGCompiler


class CompilerRegistry:
    """Registry of language-specific USIG compilers."""

    def __init__(self):
        self._compilers: Dict[str, Type] = {
            "Python": PythonUSIGCompiler,
            "Java": JavaUSIGCompiler,
            "TypeScript": TypeScriptUSIGCompiler,
        }

    def supported_languages(self) -> list[str]:
        return list(self._compilers.keys())

    def supports(self, language: str) -> bool:
        return language in self._compilers

    def get(self, language: str):
        compiler = self._compilers.get(language)

        if compiler is None:
            raise ValueError(
                f"No USIG compiler registered for language: {language}"
            )

        return compiler

    def create(
        self,
        language: str,
        repo_root: str,
    ):
        compiler_class = self.get(language)

        return compiler_class(
            repo_root
        )