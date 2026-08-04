"""Streamlit web dashboard for the AI Orchestrator.

Drives the Plan -> Code -> Deploy -> Test -> Fix pipeline phase by phase so the
UI can show live status, the files produced, and the test/fix logs.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import re

import streamlit as st

from src import agents
from src.config import settings

# --- Model / effort options -------------------------------------------------

MODEL_OPTIONS = [
    "claude-opus-5",
    "claude-sonnet-5",
    "claude-haiku-4-5",
    "claude-opus-4-8",
    "claude-fable-5",
]

# Effort is a discrete API parameter; the spec asks for a 0.1–1.0 slider, so we
# map the float onto the supported effort levels.
EFFORT_BANDS = [
    (0.2, "low"),
    (0.4, "medium"),
    (0.6, "high"),
    (0.8, "xhigh"),
    (1.0, "max"),
]


def effort_from_slider(value: float) -> str:
    """Map a 0.1–1.0 slider value onto an API effort level."""
    for threshold, level in EFFORT_BANDS:
        if value <= threshold:
            return level
    return "max"


# --- Helpers ----------------------------------------------------------------

_FILE_RE = re.compile(
    r"#\s*path:\s*(?P<path>\S+)\s*\n```[^\n]*\n(?P<body>.*?)```",
    re.DOTALL,
)


def parse_files(code_text: str) -> list[tuple[str, str]]:
    """Extract (path, content) pairs from the Coder's path-annotated output."""
    return [(m.group("path"), m.group("body").rstrip()) for m in _FILE_RE.finditer(code_text)]


def render_files(code_text: str) -> None:
    """Show generated/updated files interactively."""
    files = parse_files(code_text)
    if not files:
        st.info("Tiada fail beranotasi-path dikesan — memaparkan output mentah.")
        st.code(code_text)
        return
    st.caption(f"📄 {len(files)} fail:")
    for path, body in files:
        with st.expander(path):
            st.code(body)


# --- Page ------------------------------------------------------------------

st.set_page_config(page_title="AI Orchestrator", page_icon="🤖", layout="wide")

# Sidebar: configuration
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    default_index = MODEL_OPTIONS.index(settings.model) if settings.model in MODEL_OPTIONS else 0
    model = st.selectbox("Model", MODEL_OPTIONS, index=default_index)
    effort_value = st.slider("Effort", min_value=0.1, max_value=1.0, value=0.6, step=0.1)
    effort_level = effort_from_slider(effort_value)
    st.caption(f"Tahap effort: **{effort_level}**")
    st.divider()
    st.caption(f"Iterasi maksimum: {settings.max_iterations}")
    st.caption(f"Workspace: `{settings.workspace_dir}`")

# Main dashboard
st.title("🤖 AI Orchestrator")
st.write(
    "Bina perisian secara autonomi melalui gelung agen khusus — "
    "**Plan → Code → Deploy → Test → Fix** — sehingga ujian lulus."
)

goal = st.text_area(
    "Arahan / matlamat",
    placeholder="Contoh: Bina REST API Flask untuk senarai tugas",
    height=120,
)
run = st.button("▶️ Jalankan Orchestrator", type="primary")

PHASES = ["PLAN", "CODE", "DEPLOY", "TEST", "FIX", "COMPLETE"]

if run:
    if not goal.strip():
        st.warning("Sila masukkan arahan terlebih dahulu.")
        st.stop()

    overrides = {"model": model, "effort": effort_level}
    progress = st.progress(0.0, text="Bermula…")

    try:
        # --- PLAN ---
        progress.progress(0.1, text="Fasa: PLAN")
        with st.status("🧠 PLAN — merancang pelaksanaan…", expanded=True) as s:
            plan_text = agents.plan(goal, **overrides)
            st.markdown(plan_text)
            s.update(label="🧠 PLAN — selesai", state="complete")

        # --- CODE ---
        progress.progress(0.3, text="Fasa: CODE")
        with st.status("💻 CODE — menjana kod…") as s:
            code_text = agents.code(plan_text, **overrides)
            s.update(label="💻 CODE — selesai", state="complete")

        st.subheader("Fail dijana")
        files_placeholder = st.container()
        with files_placeholder:
            render_files(code_text)

        # --- DEPLOY / TEST / FIX loop ---
        passed = False
        iteration = 0
        while iteration < settings.max_iterations:
            iteration += 1

            progress.progress(0.5, text=f"Fasa: DEPLOY (iterasi {iteration})")
            with st.status(f"🚀 DEPLOY (iterasi {iteration})…") as s:
                artifact = agents.deploy(code_text)
                st.write(f"Artifak ditulis ke `{artifact}`")
                s.update(label=f"🚀 DEPLOY (iterasi {iteration}) — selesai", state="complete")

            progress.progress(0.7, text=f"Fasa: TEST (iterasi {iteration})")
            with st.status(f"🧪 TEST (iterasi {iteration})…") as s:
                result = agents.test(plan_text, code_text, **overrides)
                with st.expander(f"Log ujian (iterasi {iteration})", expanded=not result.passed):
                    st.markdown(result.report)
                state = "complete" if result.passed else "error"
                label = "lulus ✅" if result.passed else "gagal ❌"
                s.update(label=f"🧪 TEST (iterasi {iteration}) — {label}", state=state)

            if result.passed:
                passed = True
                break

            progress.progress(0.85, text=f"Fasa: FIX (iterasi {iteration})")
            with st.status(f"🔧 FIX (iterasi {iteration}) — membaiki…") as s:
                code_text = agents.fix(plan_text, code_text, result.report, **overrides)
                s.update(label=f"🔧 FIX (iterasi {iteration}) — selesai", state="complete")

            # Refresh the file view with the revised code.
            files_placeholder.empty()
            with files_placeholder:
                render_files(code_text)

        # --- COMPLETE ---
        progress.progress(1.0, text="Fasa: COMPLETE")
        if passed:
            st.success(f"✅ COMPLETE — ujian lulus selepas {iteration} iterasi.")
        else:
            st.error(
                f"⛔ Gelung berhenti: mencapai had {settings.max_iterations} iterasi "
                "tanpa lulus."
            )

    except Exception as exc:  # noqa: BLE001 — surface any runtime error in the UI
        progress.empty()
        st.error(f"Ralat semasa menjalankan orchestrator: {exc}")
        st.caption("Pastikan `ANTHROPIC_API_KEY` ditetapkan dalam `.env`.")
