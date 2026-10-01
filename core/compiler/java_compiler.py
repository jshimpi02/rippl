from __future__ import annotations

from pathlib import Path
from typing import Iterable

from tree_sitter import Language, Parser
import tree_sitter_java

from core.usig.factory import (
    class_node,
    edge,
    file_node,
    function_node,
    repository_node,
)
from core.usig.schema import USIGraph


class JavaUSIGCompiler:
    """Compile Java source files into Rippl's USIG representation."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.project_name = self.repo_root.name

        self.graph = USIGraph(
            project_id=f"project:{self.project_name}",
            project_name=self.project_name,
            root=str(self.repo_root),
            languages=["Java"],
        )

        self.language = Language(
            tree_sitter_java.language()
        )

        self.parser = Parser(self.language)

    def compile(self) -> USIGraph:
        repo = repository_node(
            self.project_name,
            str(self.repo_root),
        )

        self.graph.add_node(repo)

        for path in self._iter_java_files():
            self._compile_file(
                path,
                repo.id,
            )

        return self.graph

    def _iter_java_files(self) -> Iterable[Path]:
        ignored = {
            ".git",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            "target",
        }

        for path in self.repo_root.rglob("*.java"):
            if any(
                part in ignored
                for part in path.parts
            ):
                continue

            yield path

    def _compile_file(
        self,
        path: Path,
        repository_id: str,
    ) -> None:
        rel = self._rel(path)

        source_bytes = path.read_bytes()

        tree = self.parser.parse(
            source_bytes
        )

        fnode = file_node(
            rel,
            "Java",
        )

        self.graph.add_node(fnode)

        self.graph.add_edge(
            edge(
                repository_id,
                fnode.id,
                "CONTAINS",
                "repository_scanner",
            )
        )

        self._walk(
            tree.root_node,
            source_bytes,
            rel,
            fnode.id,
            current_class=None,
        )

    def _walk(
        self,
        node,
        source_bytes: bytes,
        rel: str,
        file_id: str,
        current_class: str | None,
    ) -> None:
        next_class = current_class

        if node.type == "class_declaration":
            class_name = self._child_text(
                node,
                "name",
                source_bytes,
            )

            if class_name:
                cnode = class_node(
                    rel,
                    class_name,
                    node.start_point[0] + 1,
                    node.end_point[0] + 1,
                    language="Java",
                    generated_by="java_tree_sitter_parser",
                )

                self.graph.add_node(cnode)

                self.graph.add_edge(
                    edge(
                        file_id,
                        cnode.id,
                        "DECLARES",
                        "java_tree_sitter_parser",
                    )
                )

                next_class = class_name

        elif node.type in {
            "method_declaration",
            "constructor_declaration",
        }:
            self._compile_method(
                node,
                source_bytes,
                rel,
                file_id,
                current_class,
            )

            # _compile_method handles everything inside the
            # method, so don't recursively interpret nested
            # syntax as top-level declarations.
            return

        for child in node.children:
            self._walk(
                child,
                source_bytes,
                rel,
                file_id,
                next_class,
            )

    def _compile_method(
        self,
        node,
        source_bytes: bytes,
        rel: str,
        file_id: str,
        current_class: str | None,
    ) -> None:
        method_name = self._child_text(
            node,
            "name",
            source_bytes,
        )

        if not method_name:
            return

        display_name = (
            f"{current_class}.{method_name}"
            if current_class
            else method_name
        )

        parameters = self._extract_parameters(
            node,
            source_bytes,
        )

        conditions = self._extract_conditions(
            node,
            source_bytes,
        )

        identifiers = sorted(
            self._extract_identifiers(
                node,
                source_bytes,
            )
        )

        complexity = self._estimate_complexity(
            node
        )

        method_node = function_node(
            rel,
            display_name,
            node.start_point[0] + 1,
            node.end_point[0] + 1,
            attributes={
                "parameters": parameters,
                "is_async": False,
                "parent_class": current_class,
                "conditions": conditions,
                "identifiers": identifiers,
            },
            metrics={
                "lines_of_code": max(
                    1,
                    node.end_point[0]
                    - node.start_point[0]
                    + 1,
                ),
                "cyclomatic_complexity": complexity,
            },
            language="Java",
            generated_by="java_tree_sitter_parser",
        )

        self.graph.add_node(method_node)

        self.graph.add_edge(
            edge(
                file_id,
                method_node.id,
                "DECLARES",
                "java_tree_sitter_parser",
            )
        )

    def _extract_parameters(
        self,
        node,
        source_bytes: bytes,
    ) -> list[str]:
        parameters = []

        parameter_list = node.child_by_field_name(
            "parameters"
        )

        if parameter_list is None:
            return parameters

        for child in parameter_list.children:
            if child.type in {
                "formal_parameter",
                "spread_parameter",
            }:
                name_node = child.child_by_field_name(
                    "name"
                )

                if name_node is not None:
                    parameters.append(
                        self._node_text(
                            name_node,
                            source_bytes,
                        )
                    )

        return parameters

    def _extract_conditions(
        self,
        node,
        source_bytes: bytes,
    ) -> list[dict]:
        conditions = []

        for descendant in self._descendants(node):
            if descendant.type != "if_statement":
                continue

            condition_node = (
                descendant.child_by_field_name(
                    "condition"
                )
            )

            if condition_node is None:
                continue

            expression = self._node_text(
                condition_node,
                source_bytes,
            ).strip()

            if (
                expression.startswith("(")
                and expression.endswith(")")
            ):
                expression = expression[1:-1].strip()

            conditions.append(
                {
                    "expression": expression,
                    "start_line": (
                        descendant.start_point[0] + 1
                    ),
                    "end_line": (
                        descendant.end_point[0] + 1
                    ),
                }
            )

        return conditions

    def _extract_identifiers(
        self,
        node,
        source_bytes: bytes,
    ) -> set[str]:
        identifiers = set()

        for descendant in self._descendants(node):
            if descendant.type == "identifier":
                value = self._node_text(
                    descendant,
                    source_bytes,
                )

                if value:
                    identifiers.add(value)

        return identifiers

    def _estimate_complexity(
        self,
        node,
    ) -> int:
        complexity = 1

        complexity_nodes = {
            "if_statement",
            "for_statement",
            "enhanced_for_statement",
            "while_statement",
            "do_statement",
            "catch_clause",
            "ternary_expression",
        }

        for descendant in self._descendants(node):
            if descendant.type in complexity_nodes:
                complexity += 1

            elif descendant.type == "binary_expression":
                operators = {
                    child.type
                    for child in descendant.children
                }

                if "&&" in operators or "||" in operators:
                    complexity += 1

        return complexity

    def _descendants(self, node):
        for child in node.children:
            yield child
            yield from self._descendants(child)

    def _child_text(
        self,
        node,
        field_name: str,
        source_bytes: bytes,
    ) -> str | None:
        child = node.child_by_field_name(
            field_name
        )

        if child is None:
            return None

        return self._node_text(
            child,
            source_bytes,
        )

    def _node_text(
        self,
        node,
        source_bytes: bytes,
    ) -> str:
        return source_bytes[
            node.start_byte:node.end_byte
        ].decode(
            "utf-8",
            errors="replace",
        )

    def _rel(
        self,
        path: Path,
    ) -> str:
        return str(
            path.relative_to(
                self.repo_root
            )
        ).replace("\\", "/")