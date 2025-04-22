"""Code for creating a minimal IDE in browser."""

from pathlib import Path

import st_bridge
import streamlit as st
from streamlit_ace import st_ace
from streamlit_javascript import st_javascript

_JS_CODE = Path(__file__).parent.joinpath("js", "editor.js").read_text("UTF-8").strip()


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
        base_dir.joinpath(key).write_text(code)
        st.session_state[f"{key}_hash"] = code_hash


def st_editor(base_dir: Path, files: list[str], init_data: list[str]):
    """Add an editor to the page."""
    with st.container(height=1, border=False):
        st_javascript(_JS_CODE)
        editor_height = st_bridge.bridge("editor-height", default="500")

    with st.container():
        editor_tabs = st.tabs(files)
        for file_idx, file_tab in enumerate(editor_tabs):
            with file_tab:
                _new_ace_ide(editor_height, base_dir, files[file_idx], init_data[file_idx])
