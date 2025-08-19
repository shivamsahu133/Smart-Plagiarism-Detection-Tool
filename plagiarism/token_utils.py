from __future__ import annotations

import io
import re
import tokenize
from typing import Dict, List, Tuple

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def strip_comments_and_whitespace(source: str) -> str:
    out: List[str] = []
    prev_was_nl = False
    reader = io.StringIO(source).readline
    try:
        for tok in tokenize.generate_tokens(reader):
            tok_type, tok_str, _, _, _ = tok
            if tok_type in (tokenize.COMMENT, tokenize.NL):
                continue
            if tok_type == tokenize.NEWLINE:
                if not prev_was_nl:
                    out.append("\n")
                prev_was_nl = True
                continue
            prev_was_nl = False
            out.append(tok_str)
    except Exception:
        return "\n".join(
            line.split("#", 1)[0].rstrip() for line in source.splitlines()
        )
    return "".join(out)


def normalize_identifiers(source: str) -> Tuple[str, Dict[str, str]]:
    reader = io.StringIO(source).readline
    out: List[str] = []
    name_to_generic: Dict[str, str] = {}
    next_id = 0

    def _alloc(name: str) -> str:
        nonlocal next_id
        if name not in name_to_generic:
            name_to_generic[name] = f"ID{next_id}"
            next_id += 1
        return name_to_generic[name]

    try:
        for tok in tokenize.generate_tokens(reader):
            tok_type, tok_str, _, _, _ = tok
            if tok_type == tokenize.NAME and _IDENTIFIER_RE.match(tok_str):
                out.append(_alloc(tok_str))
            elif tok_type == tokenize.COMMENT:
                continue
            else:
                out.append(tok_str)
    except Exception:
        def repl(m: re.Match[str]) -> str:
            return _alloc(m.group(0))
        return re.sub(_IDENTIFIER_RE, repl, source), name_to_generic

    return "".join(out), name_to_generic


def tokenize_code(source: str) -> List[str]:
    reader = io.StringIO(source).readline
    tokens: List[str] = []
    try:
        for tok in tokenize.generate_tokens(reader):
            tok_type, tok_str, _, _, _ = tok
            if tok_type in (tokenize.NL, tokenize.COMMENT):
                continue
            if tok_type == tokenize.NEWLINE:
                tokens.append("<NL>")
            else:
                tokens.append(tok_str)
    except Exception:
        tokens = source.split()
    return tokens
