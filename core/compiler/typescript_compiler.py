from __future__ import annotations

from pathlib import Path
from typing import Iterable

from tree_sitter import Language, Parser
import tree_sitter_typescript

from core.usig.factory import (
    class_node,
    edge,
    file_node,
    function_node,
    repository_node,
)
from core.usig.schema import USIGraph


class TypeScriptUSIGCompiler:
    """Compile TypeScript and TSX source files into USIG."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.project_name = self.repo_root.name

        self.graph = USIGraph(
            project_id=f"project:{self.project_name}",
            project_name=self.project_name,
            root=str(self.repo_root),
            languages=["TypeScript"],
        )

        self.ts_language = Language(
            tree_sitter_typescript.language_typescript()
        )

        self.tsx_language = Language(
            tree_sitter_typescript.language_tsx()
        )

    def compile(self) -> USIGraph:
        repo = repository_node(
            self.project_name,
            str(self.repo_root),
        )

        self.graph.add_node(repo)

        for path in self._iter_source_files():
            self._compile_file(
                path,
                repo.id,
            )

        return self.graph

    def _iter_source_files(self) -> Iterable[Path]:
        ignored = {
            ".git",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            "coverage",
        }

        for path in self.repo_root.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {
                ".ts",
                ".tsx",
            }:
                continue

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

        language = (
            self.tsx_language
            if path.suffix.lower() == ".tsx"
            else self.ts_language
        )

        parser = Parser(language)

        tree = parser.parse(
            source_bytes
        )

        fnode = file_node(
            rel,
            "TypeScript",
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
                    language="TypeScript",
                    generated_by="typescript_tree_sitter_parser",
                )

                self.graph.add_node(cnode)

                self.graph.add_edge(
                    edge(
                        file_id,
                        cnode.id,
                        "DECLARES",
                        "typescript_tree_sitter_parser",
                    )
                )

                next_class = class_name

        elif node.type in {
            "function_declaration",
            "method_definition",
        }:
            self._compile_function(
                node,
                source_bytes,
                rel,
                file_id,
                current_class,
            )

            return

        elif node.type in {
            "lexical_declaration",
            "variable_declaration",
        }:
            self._compile_variable_functions(
                node,
                source_bytes,
                rel,
                file_id,
                current_class,
            )

            # Continue walking because the declaration
            # may contain other relevant syntax.

        for child in node.children:
            self._walk(
                child,
                source_bytes,
                rel,
                file_id,
                next_class,
            )

    def _compile_function(
        self,
        node,
        source_bytes: bytes,
        rel: str,
        file_id: str,
        current_class: str | None,
    ) -> None:
        function_name = self._child_text(
            node,
            "name",
            source_bytes,
        )

        if not function_name:
            return

        display_name = (
            f"{current_class}.{function_name}"
            if current_class
            else function_name
        )

        self._add_function_node(
            node=node,
            source_bytes=source_bytes,
            rel=rel,
            file_id=file_id,
            function_name=display_name,
            current_class=current_class,
        )

    def _compile_variable_functions(
        self,
        declaration,
        source_bytes: bytes,
        rel: str,
        file_id: str,
        current_class: str | None,
    ) -> None:
        for child in declaration.children:
            if child.type != "variable_declarator":
                continue

            name_node = child.child_by_field_name(
                "name"
            )

            value_node = child.child_by_field_name(
                "value"
            )

            if (
                name_node is None
                or value_node is None
            ):
                continue

            if value_node.type not in {
                "arrow_function",
                "function_expression",
            }:
                continue

            function_name = self._node_text(
                name_node,
                source_bytes,
            )

            display_name = (
                f"{current_class}.{function_name}"
                if current_class
                else function_name
            )

            self._add_function_node(
                node=value_node,
                source_bytes=source_bytes,
                rel=rel,
                file_id=file_id,
                function_name=display_name,
                current_class=current_class,
            )

    def _add_function_node(
        self,
        node,
        source_bytes: bytes,
        rel: str,
        file_id: str,
        function_name: str,
        current_class: str | None,
    ) -> None:
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

        fn_node = function_node(
            rel,
            function_name,
            node.start_point[0] + 1,
            node.end_point[0] + 1,
            attributes={
                "parameters": parameters,
                "is_async": self._is_async(
                    node,
                    source_bytes,
                ),
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
            language="TypeScript",
            generated_by="typescript_tree_sitter_parser",
        )

        self.graph.add_node(fn_node)

        self.graph.add_edge(
            edge(
                file_id,
                fn_node.id,
                "DECLARES",
                "typescript_tree_sitter_parser",
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

        for child in parameter_list.named_children:
            parameter_name = self._parameter_name(
                child,
                source_bytes,
            )

            if (
                parameter_name
                and parameter_name not in parameters
            ):
                parameters.append(
                    parameter_name
                )

        return parameters

    def _parameter_name(
        self,
        node,
        source_bytes: bytes,
    ) -> str | None:
        if node.type == "identifier":
            return self._node_text(
                node,
                source_bytes,
            )

        name_node = node.child_by_field_name(
            "name"
        )

        if name_node is not None:
            return self._node_text(
                name_node,
                source_bytes,
            )

        for descendant in self._descendants(node):
            if descendant.type == "identifier":
                return self._node_text(
                    descendant,
                    source_bytes,
                )

        return None

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
            if descendant.type in {
                "identifier",
                "property_identifier",
            }:
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
            "for_in_statement",
            "while_statement",
            "do_statement",
            "catch_clause",
            "ternary_expression",
            "switch_case",
        }

        for descendant in self._descendants(node):
            if descendant.type in complexity_nodes:
                complexity += 1

            elif descendant.type == "binary_expression":
                text = self._node_text_from_node(
                    descendant
                )

                if "&&" in text:
                    complexity += text.count("&&")

                if "||" in text:
                    complexity += text.count("||")

        return complexity

    def _is_async(
        self,
        node,
        source_bytes: bytes,
    ) -> bool:
        text = self._node_text(
            node,
            source_bytes,
        ).lstrip()

        return text.startswith("async ")

    def _descendants(self, node):
        for child in node.children:
            yield child
            yield from self._descendants(
                child
            )

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

    def _node_text_from_node(
        self,
        node,
    ) -> str:
        return " ".join(
            child.type
            for child in node.children
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