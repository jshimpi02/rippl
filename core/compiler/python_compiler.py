from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from core.usig.factory import (
    business_rule_node,
    class_node,
    edge,
    file_node,
    function_node,
    repository_node,
    risk_node,
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
        repo = repository_node(self.project_name, str(self.repo_root))
        self.graph.add_node(repo)

        python_files = list(self._iter_python_files())
        parsed_files = []

        for path in python_files:
            rel = self._rel(path)
            fnode = file_node(rel, "Python")
            self.graph.add_node(fnode)
            self.graph.add_edge(edge(repo.id, fnode.id, "CONTAINS", "repository_scanner"))
            parsed = self._parse_file(path)
            if parsed is not None:
                parsed_files.append((rel, parsed, fnode.id))
                self._index_symbols(rel, parsed, fnode.id)

        for rel, tree, file_id in parsed_files:
            self._extract_edges_and_semantics(rel, tree, file_id)

        return self.graph

    def _iter_python_files(self) -> Iterable[Path]:
        ignored = {".venv", "venv", "env", "__pycache__", ".git", "node_modules"}
        for path in self.repo_root.rglob("*.py"):
            if any(part in ignored for part in path.parts):
                continue
            yield path

    def _rel(self, path: Path) -> str:
        return str(path.relative_to(self.repo_root)).replace("\\", "/")

    def _parse_file(self, path: Path) -> Optional[ast.AST]:
        try:
            return ast.parse(path.read_text(encoding="utf-8"))
        except Exception:
            return None

    def _index_symbols(self, rel: str, tree: ast.AST, file_id: str) -> None:
        collector = FunctionCollector(rel)
        collector.visit(tree)

        for cls in collector.classes:
            cnode = class_node(rel, cls.name, cls.lineno, getattr(cls, "end_lineno", cls.lineno))
            self.graph.add_node(cnode)
            self.graph.add_edge(edge(file_id, cnode.id, "DECLARES", "python_ast_parser"))

        for fn, cls_name in collector.functions:
            display_name = f"{cls_name}.{fn.name}" if cls_name else fn.name
            args = [arg.arg for arg in fn.args.args]
            loc = max(1, getattr(fn, "end_lineno", fn.lineno) - fn.lineno + 1)
            complexity = self._estimate_complexity(fn)
            fnode = function_node(
                rel,
                display_name,
                fn.lineno,
                getattr(fn, "end_lineno", fn.lineno),
                attributes={"parameters": args, "is_async": isinstance(fn, ast.AsyncFunctionDef), "parent_class": cls_name},
                metrics={"lines_of_code": loc, "cyclomatic_complexity": complexity},
            )
            self.graph.add_node(fnode)
            self.function_index[f"{rel}.{display_name}"] = fnode.id
            self.short_function_index.setdefault(fn.name, []).append(fnode.id)
            self.graph.add_edge(edge(file_id, fnode.id, "DECLARES", "python_ast_parser"))
            if cls_name:
                class_id = f"class:{rel}.{cls_name}".replace(" ", "_")

    def _extract_edges_and_semantics(self, rel: str, tree: ast.AST, file_id: str) -> None:
        collector = FunctionCollector(rel)
        collector.visit(tree)

        for fn, cls_name in collector.functions:
            display_name = f"{cls_name}.{fn.name}" if cls_name else fn.name
            source_id = self.function_index.get(f"{rel}.{display_name}")
            if not source_id:
                continue

            calls = CallCollector()
            calls.visit(fn)
            for call_name in calls.calls:
                target_candidates = self.short_function_index.get(call_name.split(".")[-1], [])
                for target_id in target_candidates:
                    if target_id != source_id:
                        self.graph.add_edge(edge(source_id, target_id, "CALLS", "python_ast_call_analyzer", confidence=0.75, evidence=call_name))

            self._extract_business_rules(rel, fn, source_id)
            self._extract_risks(rel, fn, source_id)

    def _estimate_complexity(self, node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.IfExp, ast.ExceptHandler)):
                complexity += 1
        return complexity

    def _extract_business_rules(self, rel: str, fn: ast.AST, source_id: str) -> None:
        for node in ast.walk(fn):
            if isinstance(node, ast.If):
                condition = ast.unparse(node.test) if hasattr(ast, "unparse") else "conditional expression"
                rule_key = f"{rel}.{getattr(fn, 'name', 'function')}.{node.lineno}.rule"
                title = self._title_from_condition(condition)
                desc = f"When `{condition}` is true, this function follows a distinct business or validation path."
                rule = business_rule_node(rule_key, title, desc, rel, node.lineno, getattr(node, "end_lineno", node.lineno), 0.68, condition)
                self.graph.add_node(rule)
                self.graph.add_edge(edge(source_id, rule.id, "IMPLEMENTS_RULE", "heuristic_business_rule_extractor", confidence=0.68, evidence=condition))

    def _title_from_condition(self, condition: str) -> str:
        lowered = condition.lower()
        if "premium" in lowered:
            return "Premium Customer Rule"
        if "age" in lowered or "senior" in lowered:
            return "Age-Based Eligibility Rule"
        if "status" in lowered:
            return "Status Validation Rule"
        if "total" in lowered or "amount" in lowered or "price" in lowered:
            return "Amount-Based Calculation Rule"
        return "Conditional Business Rule"

    def _extract_risks(self, rel: str, fn: ast.AST, source_id: str) -> None:
        complexity = self._estimate_complexity(fn)
        if complexity >= 6:
            risk = risk_node(
                f"{rel}.{getattr(fn, 'name', 'function')}.complexity",
                "High Branching Complexity",
                "This function contains several decision paths, increasing regression risk.",
                "Add boundary and branch-coverage tests before modifying this function.",
                rel,
                getattr(fn, "lineno", 1),
                getattr(fn, "end_lineno", getattr(fn, "lineno", 1)),
                min(0.95, 0.45 + complexity / 20),
                f"cyclomatic_complexity={complexity}",
            )
            self.graph.add_node(risk)
            self.graph.add_edge(edge(source_id, risk.id, "HAS_RISK", "risk_pass", confidence=0.85))

        source_text = ast.unparse(fn) if hasattr(ast, "unparse") else ""
        if any(token in source_text.lower() for token in ["price", "amount", "total", "tax", "discount", "payment"]):
            risk = risk_node(
                f"{rel}.{getattr(fn, 'name', 'function')}.financial_logic",
                "Financial Logic Risk",
                "This function appears to handle financial calculations or payment-related decisions.",
                "Add regression tests for rounding, boundary values, and invalid inputs.",
                rel,
                getattr(fn, "lineno", 1),
                getattr(fn, "end_lineno", getattr(fn, "lineno", 1)),
                0.72,
                "financial keywords detected",
            )
            self.graph.add_node(risk)
            self.graph.add_edge(edge(source_id, risk.id, "HAS_RISK", "risk_pass", confidence=0.8))
