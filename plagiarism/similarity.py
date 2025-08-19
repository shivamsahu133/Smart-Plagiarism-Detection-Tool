from __future__ import annotations

from difflib import SequenceMatcher
from typing import Iterable, Tuple

from .ast_utils import ast_structure_signature, sequence_similarity
from .token_utils import tokenize_code


def _ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    return float(SequenceMatcher(a=a, b=b).ratio())


def type1_similarity(a: str, b: str) -> float:
    return _ratio(a, b)


def type2_similarity(a: str, b: str) -> float:
    return _ratio(a, b)


def type3_similarity(a: str, b: str) -> float:
    ta = tokenize_code(a)
    tb = tokenize_code(b)
    return float(SequenceMatcher(a=ta, b=tb).ratio())


def type4_similarity(a: str, b: str) -> float:
    sig_a = ast_structure_signature(a)
    sig_b = ast_structure_signature(b)
    return sequence_similarity(sig_a, sig_b)


def combined_similarity(t1: float, t2: float, t3: float, t4: float, weights: Tuple[float, float, float, float]) -> float:
    w1, w2, w3, w4 = weights
    total = w1 + w2 + w3 + w4
    if total <= 0:
        return 0.0
    return (w1 * t1 + w2 * t2 + w3 * t3 + w4 * t4) / total
