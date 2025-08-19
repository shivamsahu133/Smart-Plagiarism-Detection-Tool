from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, List, Tuple

from .preprocess import preprocess_for_type1, preprocess_for_type2, preprocess_for_type3
from .ast_utils import get_functions
from .similarity import (
    type1_similarity,
    type2_similarity,
    type3_similarity,
    type4_similarity,
    combined_similarity,
)


@dataclass
class AnalyzedFile:
    name: str
    source: str
    t1: str
    t2: str
    t3: str


def _prepare_files(files: Dict[str, str]) -> List[AnalyzedFile]:
    prepared: List[AnalyzedFile] = []
    for name, source in files.items():
        t1 = preprocess_for_type1(source)
        t2, _ = preprocess_for_type2(source)
        t3 = preprocess_for_type3(source)
        prepared.append(AnalyzedFile(name=name, source=source, t1=t1, t2=t2, t3=t3))
    return prepared


def _similarity_between_files(a: AnalyzedFile, b: AnalyzedFile, weights: Tuple[float, float, float, float]) -> Dict:
    s1 = type1_similarity(a.t1, b.t1)
    s2 = type2_similarity(a.t2, b.t2)
    s3 = type3_similarity(a.t3, b.t3)
    s4 = type4_similarity(a.source, b.source)
    return {
        "file_a": a.name,
        "file_b": b.name,
        "type1": s1,
        "type2": s2,
        "type3": s3,
        "type4": s4,
        "combined": combined_similarity(s1, s2, s3, s4, weights),
    }


def _similarity_between_functions(file_a: str, file_b: str, fa_source: str, fb_source: str, weights: Tuple[float, float, float, float], func_a_name: str, func_b_name: str) -> Dict:
    t1a = preprocess_for_type1(fa_source)
    t1b = preprocess_for_type1(fb_source)
    t2a, _ = preprocess_for_type2(fa_source)
    t2b, _ = preprocess_for_type2(fb_source)
    t3a = preprocess_for_type3(fa_source)
    t3b = preprocess_for_type3(fb_source)

    s1 = type1_similarity(t1a, t1b)
    s2 = type2_similarity(t2a, t2b)
    s3 = type3_similarity(t3a, t3b)
    s4 = type4_similarity(fa_source, fb_source)

    return {
        "file_a": file_a,
        "func_a": func_a_name,
        "file_b": file_b,
        "func_b": func_b_name,
        "type1": s1,
        "type2": s2,
        "type3": s3,
        "type4": s4,
        "combined": combined_similarity(s1, s2, s3, s4, weights),
        "source_a": fa_source,
        "source_b": fb_source,
    }


def analyze_files(files: Dict[str, str], weights: Tuple[float, float, float, float] = (0.25, 0.25, 0.25, 0.25)) -> Dict:
    prepared = _prepare_files(files)

    file_pairs: List[Dict] = []
    for a, b in combinations(prepared, 2):
        file_pairs.append(_similarity_between_files(a, b, weights))

    function_pairs: List[Dict] = []
    file_to_functions = {name: get_functions(src, filename=name) for name, src in files.items()}
    names = list(files.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            fa_list = file_to_functions.get(names[i], [])
            fb_list = file_to_functions.get(names[j], [])
            for fa in fa_list:
                for fb in fb_list:
                    function_pairs.append(
                        _similarity_between_functions(
                            file_a=fa.filename,
                            file_b=fb.filename,
                            fa_source=fa.source,
                            fb_source=fb.source,
                            weights=weights,
                            func_a_name=fa.name,
                            func_b_name=fb.name,
                        )
                    )

    file_pairs.sort(key=lambda r: r["combined"], reverse=True)
    function_pairs.sort(key=lambda r: r["combined"], reverse=True)

    return {"file_pairs": file_pairs, "function_pairs": function_pairs}
