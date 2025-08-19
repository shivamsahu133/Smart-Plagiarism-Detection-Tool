import io
from typing import Dict, List, Tuple

import streamlit as st

from plagiarism.compare import analyze_files
from plagiarism.highlight import html_side_by_side_diff

# --- New: Gemini API imports/config ---
import google.generativeai as genai

API_KEY = "AIzaSyCD6GTvCElDOegXZd4pU5xQah8DUgGB7rU"
genai.configure(api_key=API_KEY)


st.set_page_config(
    page_title="Code Plagiarism Detection Tool",
    layout="wide",
    initial_sidebar_state="expanded",
)


def detect_ai_generated(text: str) -> str:
    """Return 'AI' or 'Human' by asking Gemini; defaults to 'Human' on errors.

    The model is instructed to reply ONLY with 'AI' or 'Human'.
    """
    text = (text or "").strip()
    if not text:
        return "Human"
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = (
            "Analyze the following text and respond ONLY with 'AI' or 'Human'.\n\n" + text
        )
        resp = model.generate_content(prompt)
        raw = (resp.text or "").strip()
        if "ai" == raw.lower():
            return "AI"
        if "human" == raw.lower():
            return "Human"
        # Fallback: heuristic parsing
        return "AI" if "ai" in raw.lower() else "Human"
    except Exception:
        return "Human"


def _init_state() -> None:
    """Initialize Streamlit session state keys."""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []  # List[Dict[name,str content]]
    if "analysis_results" not in st.session_state:
        st.session_state.analysis_results = None
    if "last_run_params" not in st.session_state:
        st.session_state.last_run_params = {}


def _store_uploads(files: List[Tuple[str, str]]) -> None:
    st.session_state.uploaded_files = [
        {"name": name, "content": content} for name, content in files
    ]


def _read_uploaded_files(uploaded) -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    for uf in uploaded:
        try:
            content = uf.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")
            files.append((uf.name, content))
        except Exception as exc:  # pragma: no cover - UI path
            st.warning(f"Failed to read {uf.name}: {exc}")
    return files


def _render_header() -> None:
    st.title("🔎 Code Plagiarism Detection Tool")
    st.caption(
        "Detect Type-1..4 code clones with preprocessing, token, and AST-based heuristics"
    )


def _render_sidebar() -> Dict:
    st.sidebar.header("Settings")
    min_similarity = st.sidebar.slider(
        "Minimum similarity to show (combined %)", 0, 100, 40, step=5
    )
    max_pairs = st.sidebar.slider("Max function pairs to display", 10, 500, 100, step=10)
    weights_col1, weights_col2 = st.sidebar.columns(2)
    with weights_col1:
        w1 = st.number_input("Type-1 weight", 0.0, 1.0, 0.25, 0.05)
        w2 = st.number_input("Type-2 weight", 0.0, 1.0, 0.25, 0.05)
    with weights_col2:
        w3 = st.number_input("Type-3 weight", 0.0, 1.0, 0.25, 0.05)
        w4 = st.number_input("Type-4 weight", 0.0, 1.0, 0.25, 0.05)
        sum_w = w1 + w2 + w3 + w4
        if sum_w == 0:
            w1, w2, w3, w4 = 0.25, 0.25, 0.25, 0.25
            st.sidebar.info("Weights normalized to equal parts.")

    search_query = st.sidebar.text_input("Filter by file/function name contains", "")

    return {
        "min_similarity": min_similarity,
        "max_pairs": max_pairs,
        "weights": (w1, w2, w3, w4),
        "search": search_query.strip().lower(),
    }


def _render_upload_tab(settings: Dict) -> None:
    uploaded = st.file_uploader(
        "Upload one or more Python source files",
        type=["py"],
        accept_multiple_files=True,
        key="uploader",
    )

    if uploaded:
        files = _read_uploaded_files(uploaded)
        if files:
            _store_uploads(files)
            st.success(f"Loaded {len(files)} files.")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Analyze", type="primary", use_container_width=True):
            if not st.session_state.uploaded_files:
                st.warning("Please upload files first.")
                return
            with st.spinner("Analyzing code for similarities..."):
                files_map = {f["name"]: f["content"] for f in st.session_state.uploaded_files}
                results = analyze_files(
                    files_map,
                    weights=settings["weights"],
                )
                st.session_state.analysis_results = results
                st.session_state.last_run_params = settings
            st.success("Analysis complete.")
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.uploaded_files = []
            st.session_state.analysis_results = None
            st.experimental_rerun()

    if st.session_state.uploaded_files:
        st.subheader("Uploaded Files")
        for item in st.session_state.uploaded_files:
            with st.expander(item["name"], expanded=False):
                st.code(item["content"], language="python")


def _render_results_tab(settings: Dict) -> None:
    results = st.session_state.analysis_results
    if not results:
        st.info("Run an analysis first in the Upload & Analyze tab.")
        return

    file_pairs = results["file_pairs"]
    func_pairs = results["function_pairs"]

    st.subheader("File Pair Similarities")

    # Filter
    min_sim = settings["min_similarity"]/100.0
    search = settings["search"]

    def passes_filter(row: Dict) -> bool:
        name_blob = f"{row['file_a']} {row['file_b']}".lower()
        return (row["combined"] >= min_sim) and (search in name_blob)

    filtered_file_pairs = [r for r in file_pairs if passes_filter(r)]

    # Display table
    def _format_pct(x: float) -> str:
        return f"{round(100.0 * x, 1)}%"

    if filtered_file_pairs:
        st.dataframe(
            [
                {
                    "File A": r["file_a"],
                    "File B": r["file_b"],
                    "Type-1": _format_pct(r["type1"]),
                    "Type-2": _format_pct(r["type2"]),
                    "Type-3": _format_pct(r["type3"]),
                    "Type-4": _format_pct(r["type4"]),
                    "Combined": _format_pct(r["combined"]),
                }
                for r in filtered_file_pairs
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No file pairs match the filters.")

    st.divider()
    st.subheader("Function-level Similarities")

    def func_passes_filter(row: Dict) -> bool:
        name_blob = f"{row['file_a']} {row['func_a']} {row['file_b']} {row['func_b']}".lower()
        return (row["combined"] >= min_sim) and (search in name_blob)

    filtered_func_pairs = [r for r in func_pairs if func_passes_filter(r)]
    filtered_func_pairs.sort(key=lambda r: r["combined"], reverse=True)
    filtered_func_pairs = filtered_func_pairs[: settings["max_pairs"]]

    if filtered_func_pairs:
        st.dataframe(
            [
                {
                    "File A": r["file_a"],
                    "Function A": r["func_a"],
                    "File B": r["file_b"],
                    "Function B": r["func_b"],
                    "Type-1": _format_pct(r["type1"]),
                    "Type-2": _format_pct(r["type2"]),
                    "Type-3": _format_pct(r["type3"]),
                    "Type-4": _format_pct(r["type4"]),
                    "Combined": _format_pct(r["combined"]),
                }
                for r in filtered_func_pairs
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption("Top matches by combined similarity.")
    else:
        st.info("No function pairs match the filters.")

    csv_bytes = io.StringIO()
    if file_pairs:
        csv_bytes.write("file_a,file_b,type1,type2,type3,type4,combined\n")
        for r in file_pairs:
            csv_bytes.write(
                ",".join(
                    [
                        r["file_a"],
                        r["file_b"],
                        str(round(100.0 * r["type1"], 2)),
                        str(round(100.0 * r["type2"], 2)),
                        str(round(100.0 * r["type3"], 2)),
                        str(round(100.0 * r["type4"], 2)),
                        str(round(100.0 * r["combined"], 2)),
                    ]
                )
                + "\n"
            )
        st.download_button(
            "Download file pair results (CSV)", data=csv_bytes.getvalue(), file_name="file_pairs.csv"
        )


def _render_viewer_tab() -> None:
    results = st.session_state.analysis_results
    if not results:
        st.info("Run an analysis first in the Upload & Analyze tab.")
        return

    func_pairs = results["function_pairs"]
    if not func_pairs:
        st.info("No function-level matches found.")
        return

    func_pairs_sorted = sorted(func_pairs, key=lambda r: r["combined"], reverse=True)
    options = [
        f"{r['file_a']}::{r['func_a']}  ↔  {r['file_b']}::{r['func_b']}  ({round(100*r['combined'],1)}%)"
        for r in func_pairs_sorted
    ]
    choice = st.selectbox("Choose a function pair to view", options=options, index=0)
    selected = func_pairs_sorted[options.index(choice)]

    left, right = st.columns(2)
    with left:
        st.caption(f"{selected['file_a']} :: {selected['func_a']}")
    with right:
        st.caption(f"{selected['file_b']} :: {selected['func_b']}")

    html = html_side_by_side_diff(
        selected["source_a"], selected["source_b"], context=True, numlines=2
    )
    st.components.v1.html(html, height=600, scrolling=True)


# --- New: AI Text Detection UI ---

def _render_ai_text_detection() -> None:
    st.header("AI Text Detection Tool 🔍")
    text = st.text_area("Enter text to analyze", height=200, key="ai_text_input")
    if st.button("Check", key="ai_text_check_btn"):
        with st.spinner("Contacting Gemini..."):
            verdict = detect_ai_generated(text)
        if verdict == "AI":
            st.error("⚠️ This text looks AI-generated.")
        else:
            st.success("✅ This text looks Human-written.")


def main() -> None:  # pragma: no cover - Streamlit entry
    _init_state()

    page = st.sidebar.radio(
        "Choose Tool",
        ("Code Plagiarism Detection", "AI Text Detection"),
        index=0,
    )

    if page == "Code Plagiarism Detection":
        _render_header()
        settings = _render_sidebar()
        tab_upload, tab_results, tab_viewer = st.tabs(
            ["Upload & Analyze", "Results", "Side-by-side Viewer"]
        )
        with tab_upload:
            _render_upload_tab(settings)
        with tab_results:
            _render_results_tab(settings)
        with tab_viewer:
            _render_viewer_tab()
    else:
        _render_ai_text_detection()


if __name__ == "__main__":  # pragma: no cover
    main()
