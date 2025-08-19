from difflib import HtmlDiff
from typing import Iterable


def html_side_by_side_diff(source_a: str, source_b: str, context: bool = True, numlines: int = 2) -> str:
    """Return an HTML page with side-by-side diff highlighting between two sources.

    Parameters
    ----------
    source_a : str
        Left side source code.
    source_b : str
        Right side source code.
    context : bool
        If True, show contextual (collapsed) diff.
    numlines : int
        Number of context lines to include around differences.
    """
    a_lines: Iterable[str] = source_a.splitlines()
    b_lines: Iterable[str] = source_b.splitlines()
    differ = HtmlDiff(wrapcolumn=100)
    return differ.make_file(a_lines, b_lines, "A", "B", context=context, numlines=numlines)
