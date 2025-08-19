from __future__ import annotations

import re
from typing import Dict, Tuple

from .token_utils import strip_comments_and_whitespace, normalize_identifiers

_FOR_WHILE_RE = re.compile(r"\b(for|while)\b", re.IGNORECASE)


def normalize_loops(source: str) -> str:
    return _FOR_WHILE_RE.sub("LOOP", source)


def preprocess_for_type1(source: str) -> str:
    return strip_comments_and_whitespace(source)


def preprocess_for_type2(source: str) -> Tuple[str, Dict[str, str]]:
    t1 = preprocess_for_type1(source)
    norm, mapping = normalize_identifiers(t1)
    return norm, mapping


def preprocess_for_type3(source: str) -> str:
    t1 = preprocess_for_type1(source)
    t2, _ = normalize_identifiers(t1)
    t3 = normalize_loops(t2)
    return t3
