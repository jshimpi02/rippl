from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from core.usig.factory import (
    class_node,
    edge,
    file_node,
    function_node,
    repository_node,
)
from core.usig.schema import USIGraph


class FunctionCollector(ast.NodeVisitor):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.functions: List[Tuple[ast.AST, Optional[str]]] = []
        self.classes: List[ast.ClassDef] = []
        self.class_stack: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(node)
        self.class_stack.append(node.name)
        self.generic_visit(node)
        self.class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        class_name = self.class_stack[-1] if self.class_stack else None
        self.functions.append((node, class_name))
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        class_name = self.class_stack[-1] if self.class_stack else None
        self.functions.append((node, class_name))
        self.generic_visit(node)


class CallCollector(ast.NodeVisitor):
    def __init__(self):
        self.calls: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        name = self._call_name(node.func)

        if name:
            self.calls.add(name)

        self.generic_visit(node)

    def _call_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            base = self._call_name(node.value)
            return f"{base}.{node.attr}" if base else node.attr

        return None

class IdentifierCollector(ast.NodeVisitor):
    """Collect identifiers referenced inside a function."""

    def __init__(self):
        self.identifiers: Set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        self.identifiers.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        self.identifiers.add(node.attr)
        self.generic_visit(node)
        
class PythonUSIGCompiler:
    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.project_name = self.repo_root.name

        self.graph = USIGraph(
            project_id=f"project:{self.project_name}",
            project_name=self.project_name,
            root=str(self.repo_root),
            languages=["Python"],
        )

        self.function_index: Dict[str, str] = {}
        self.short_function_index: Dict[str, List[str]] = {}

    def compile(self) -> USIGraph:
        repo = repository_node(
            self.project_name,
            str(self.repo_root),
        )

        self.graph.add_node(repo)

        python_files = list(self._iter_python_files())
        parsed_files = []

        for path in python_files:
            rel = self._rel(path)

            fnode = file_node(
                rel,
                "Python",
            )

            self.graph.add_node(fnode)

            self.graph.add_edge(
                edge(
                    repo.id,
                    fnode.id,
                    "CONTAINS",
                    "repository_scanner",
                )
            )

            parsed = self._parse_file(path)

            if parsed is not None:
                parsed_files.append(
                    (
                        rel,
                        parsed,
                        fnode.id,
                    )
                )

                self._index_symbols(
                    rel,
                    parsed,
                    fnode.id,
                )

        for rel, tree, file_id in parsed_files:
            self._extract_edges_and_semantics(
                rel,
                tree,
                file_id,
            )

        return self.graph

    def _iter_python_files(self) -> Iterable[Path]:
        ignored = {
            ".venv",
            "venv",
            "env",
            "__pycache__",
            ".git",
            "node_modules",
        }

        for path in self.repo_root.rglob("*.py"):
            if any(part in ignored for part in path.parts):
                continue

            yield path

    def _rel(self, path: Path) -> str:
        return str(
            path.relative_to(self.repo_root)
        ).replace("\\", "/")

    def _parse_file(self, path: Path) -> Optional[ast.AST]:
        try:
            return ast.parse(
                path.read_text(encoding="utf-8")
            )
        except Exception:
            return None

    def _index_symbols(
        self,
        rel: str,
        tree: ast.AST,
        file_id: str,
    ) -> None:
        collector = FunctionCollector(rel)
        collector.visit(tree)

        for cls in collector.classes:
            cnode = class_node(
                rel,
                cls.name,
                cls.lineno,
                getattr(
                    cls,
                    "end_lineno",
                    cls.lineno,
                ),
            )

            self.graph.add_node(cnode)

            self.graph.add_edge(
                edge(
                    file_id,
                    cnode.id,
                    "DECLARES",
                    "python_ast_parser",
                )
            )

        for fn, cls_name in collector.functions:
            display_name = (
                f"{cls_name}.{fn.name}"
                if cls_name
                else fn.name
            )

            args = [
                arg.arg
                for arg in fn.args.args
            ]

            loc = max(
                1,
                getattr(
                    fn,
                    "end_lineno",
                    fn.lineno,
                )
                - fn.lineno
                + 1,
            )

            complexity = self._estimate_complexity(fn)

            identifier_collector = IdentifierCollector()
            identifier_collector.visit(fn)

            identifiers = sorted(identifier_collector.identifiers)

            conditions = []

            for node in ast.walk(fn):
                if isinstance(node, ast.If):
                    condition = (
                        ast.unparse(node.test)
                        if hasattr(ast, "unparse")
                        else "conditional expression"
                    )

                    conditions.append(
                        {
                            "expression": condition,
                            "start_line": node.lineno,
                            "end_line": getattr(
                                node,
                                "end_lineno",
                                node.lineno,
                            ),
                        }
                    )

            fnode = function_node(
                rel,
                display_name,
                fn.lineno,
                getattr(
                    fn,
                    "end_lineno",
                    fn.lineno,
                ),
                attributes={
                    "parameters": args,
                    "is_async": isinstance(
                        fn,
                        ast.AsyncFunctionDef,
                    ),
                    "parent_class": cls_name,
                    "conditions": conditions,
                    "identifiers": identifiers,
                },
                metrics={
                    "lines_of_code": loc,
                    "cyclomatic_complexity": complexity,
                },
            )

            self.graph.add_node(fnode)

            self.function_index[
                f"{rel}.{display_name}"
            ] = fnode.id

            self.short_function_index.setdefault(
                fn.name,
                [],
            ).append(fnode.id)

            self.graph.add_edge(
                edge(
                    file_id,
                    fnode.id,
                    "DECLARES",
                    "python_ast_parser",
                )
            )

            if cls_name:
                class_id = (
                    f"class:{rel}.{cls_name}"
                ).replace(" ", "_")

    def _extract_edges_and_semantics(
        self,
        rel: str,
        tree: ast.AST,
        file_id: str,
    ) -> None:
        collector = FunctionCollector(rel)
        collector.visit(tree)

        for fn, cls_name in collector.functions:
            display_name = (
                f"{cls_name}.{fn.name}"
                if cls_name
                else fn.name
            )

            source_id = self.function_index.get(
                f"{rel}.{display_name}"
            )

            if not source_id:
                continue

            calls = CallCollector()
            calls.visit(fn)

            for call_name in calls.calls:
                target_candidates = (
                    self.short_function_index.get(
                        call_name.split(".")[-1],
                        [],
                    )
                )

                for target_id in target_candidates:
                    if target_id != source_id:
                        self.graph.add_edge(
                            edge(
                                source_id,
                                target_id,
                                "CALLS",
                                "python_ast_call_analyzer",
                                confidence=0.75,
                                evidence=call_name,
                            )
                        )

    def _estimate_complexity(
        self,
        node: ast.AST,
    ) -> int:
        complexity = 1

        for child in ast.walk(node):
            if isinstance(
                child,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.Try,
                    ast.BoolOp,
                    ast.IfExp,
                    ast.ExceptHandler,
                ),
            ):
                complexity += 1

        return complexity

    