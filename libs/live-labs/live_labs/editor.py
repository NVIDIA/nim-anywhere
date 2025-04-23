"""Code for creating a minimal IDE in browser."""

from pathlib import Path

import st_bridge
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from streamlit_ace import st_ace
from streamlit_javascript import st_javascript

_JS_CODE = Path(__file__).parent.joinpath("js", "editor.js").read_text("UTF-8").strip()
_CSS = Path(__file__).parent.joinpath("css", "editor.css").read_text("UTF-8").strip()


def _new_ace_ide(editor_height: str, base_dir: Path, key: str, value: str) -> None:
    """Create the streamlit object and sync with  filesystem."""
    code = st_ace(
        value=value,
        placeholder="Write your code here.",
        height=f"{editor_height}px",
        font_size=20,
        language="python",
        theme="crimson_editor",
        key=key,
        show_print_margin=True,
        auto_update=True,
    )

    last_code_hash = st.session_state.get(f"{key}_hash", "")
    code_hash = hash(code)

    if last_code_hash != code_hash:
        st.session_state["code_change_derived"] = True
        base_dir.joinpath(key).write_text(code)
        st.session_state[f"{key}_hash"] = code_hash


def st_editor(base_dir: Path, files: list[str], init_data: list[str]) -> DeltaGenerator:
    """Add an editor to the page."""
    with st.container(height=1, border=False):
        st_javascript(_JS_CODE, key="editor")
        st.html(f"<style>{_CSS}</style>")
        editor_height = st_bridge.bridge("editor-height", default="500")

    with st.container():
        tab_names = [f":material/data_object: {fname}" for fname in files] + [":material/terminal: Terminal Output"]
        editor_tabs = st.tabs(tab_names)
        for file_idx, file_tab in enumerate(editor_tabs[:-1]):
            with file_tab:
                _new_ace_ide(editor_height, base_dir, files[file_idx], init_data[file_idx])

    return editor_tabs[-1]
