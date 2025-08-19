from __future__ import annotations

import ast
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable, List


@dataclass
class FunctionInfo:
    filename: str
    name: str
    start_line: int
    end_line: int
    source: str


def _safe_end_lineno(node: ast.AST) -> int:
    end = getattr(node, "end_lineno", None)
    if isinstance(end, int):
        return end
    last = None
    for child in ast.walk(node):
        lineno = getattr(child, "lineno", None)
        if isinstance(lineno, int):
            if last is None or lineno > last:
                last = lineno
    return last or getattr(node, "lineno", 1)


def extract_source_by_lines(source: str, start_line: int, end_line: int) -> str:
    lines = source.splitlines()
    start = max(1, start_line) - 1
    end = max(start, end_line)
    return "\n".join(lines[start:end])


def get_functions(source: str, filename: str = "<memory>") -> List[FunctionInfo]:
    try:
        tree = ast.parse(source)
    except Exception:
        return []

    functions: List[FunctionInfo] = []

    class _Collector(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
            start = node.lineno
            end = _safe_end_lineno(node)
            functions.append(
                FunctionInfo(
                    filename=filename,
                    name=node.name,
                    start_line=start,
                    end_line=end,
                    source=extract_source_by_lines(source, start, end),
                )
            )
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
            self.visit_FunctionDef(node)  # type: ignore[arg-type]

    _Collector().visit(tree)
    return functions


def _node_tag(node: ast.AST) -> str:
    if isinstance(node, (ast.For, ast.While)):
        return "LOOP"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return "FUNC"
    if isinstance(node, ast.If):
        return "IF"
    if isinstance(node, ast.Call):
        return "CALL"
    if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        return "ASSIGN"
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return "COMP"
    if isinstance(node, ast.BinOp):
        return "BINOP"
    if isinstance(node, ast.UnaryOp):
        return "UNARYOP"
    if isinstance(node, ast.BoolOp):
        return "BOOLOP"
    if isinstance(node, ast.Compare):
        return "COMPARE"
    if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
        return "RETURN"
    if isinstance(node, (ast.With, ast.AsyncWith)):
        return "WITH"
    if isinstance(node, (ast.Try,)):
        return "TRY"
    if isinstance(node, (ast.Raise,)):
        return "RAISE"
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return "IMPORT"
    if isinstance(node, ast.Attribute):
        return "ATTR"
    if isinstance(node, ast.Name):
        return "NAME"
    if isinstance(node, ast.Constant):
        return "CONST"
    return type(node).__name__.upper()


def ast_structure_signature(source: str) -> List[str]:
    try:
        tree = ast.parse(source)
    except Exception:
        return []

    tags: List[str] = []

    class _Sig(ast.NodeVisitor):
        def generic_visit(self, node: ast.AST) -> None:  # type: ignore[override]
            tags.append(_node_tag(node))
            super().generic_visit(node)

    _Sig().visit(tree)
    return tags


def sequence_similarity(a: Iterable[str], b: Iterable[str]) -> float:
    a_list = list(a)
    b_list = list(b)
    if not a_list and not b_list:
        return 1.0
    matcher = SequenceMatcher(a=a_list, b=b_list)
    return float(matcher.ratio())


def function_name_similarity(name_a: str, name_b: str) -> float:
    return float(SequenceMatcher(a=name_a.lower(), b=name_b.lower()).ratio())
