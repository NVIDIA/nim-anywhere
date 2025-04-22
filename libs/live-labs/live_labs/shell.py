"""Tooling for loading and rendering the custom sidebar."""

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import streamlit as st
from pydantic import BaseModel
from pydantic_yaml import parse_yaml_raw_as

from live_labs.pages import settings

if TYPE_CHECKING:
    from streamlit.navigation.page import StreamlitPage

_BASE_URL = os.environ.get("PROXY_PREFIX", "")
_SETTINGS_PATH = Path(settings.__file__)

DEFAULT_CSS = Path(__file__).parent.joinpath("css", "style.css")
PREVIOUS = "Previous"
NEXT = "Next"


class MenuItem(BaseModel):
    """Representation of an item in a menu."""

    label: str
    target: str
    show_progress: bool = True

    @property
    def progress_string(self) -> str:
        """Calculate the progress indicator."""
        if not self.show_progress:
            return ""
        completed = st.session_state.get(f"{self.target}_completed", 0)
        total = st.session_state.get(f"{self.target}_total", None)

        if total is None:
            return "*(not started)*"
        if completed == total:
            return "✅"
        return f"*({completed}/{total})*"

    @property
    def full_label(self) -> str:
        """Calculate the full label with progress."""
        return f"{self.label} {self.progress_string}"

    @property
    def filepath(self) -> str:
        """Calculate the ASSUMED file path to the module."""
        return f"pages/{self.target}.py"

    @property
    def markdown(self) -> str:
        """Calculate markdown for link to URL."""
        return f"[{self.label}]({self.target})"


class Menu(BaseModel):
    """Representation of a menu."""

    label: str
    children: list[MenuItem]


class Links(BaseModel):
    """Representation of links."""

    documentation: None | str = None
    gethelp: None | str = None
    about: None | str = None
    bugs: None | str = None
    settings: None | str = None


def _icon(name: str) -> str:
    """Generate a span object for a Material Symbols Rounded icon."""
    style = (
        'style="display: inline-block; font-family: &quot;Material Symbols Rounded&quot;; font-weight: 400; '
        'user-select: none; vertical-align: bottom; white-space: nowrap; overflow-wrap: normal;"'
    )
    return f'<span role="img" { style }>{name}</span>'


class AppShell(BaseModel):
    """Representation of a sidebar structure."""

    header: str | None = None
    page_layout: Literal["centered", "wide"] = "centered"
    navbar: list[Menu]
    links: Links

    def model_post_init(self, _: Any, /) -> None:
        """Initialize streamlit."""
        st.set_page_config(
            page_title=self.header,
            layout=self.page_layout,
            menu_items={
                "Get help": self.links.gethelp,
                "Report a bug": self.links.bugs,
                "About": self.links.about,
            },
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "AppShell":
        """Load the sidebar data from yaml."""
        with open(path, "r", encoding="UTF-8") as ptr:
            yml = ptr.read()

        return parse_yaml_raw_as(cls, yml)

    @property
    def page_list(self) -> list["StreamlitPage"]:
        """Return a list of streamlit pages for multipage nav."""
        return [
            st.Page(f"pages/{item.target}.py", title=item.target) for menu in self.navbar for item in menu.children
        ] + [st.Page(_SETTINGS_PATH, title="settings")]

    def neighbors(self, page_name: str) -> tuple[str | None, str | None]:
        """Determine the next and previous pages from page_name."""
        all_pages = [f"pages/{item.target}.py" for menu in self.navbar for item in menu.children]

        try:
            page_idx = all_pages.index(f"pages/{page_name}.py")
        except ValueError:
            return None, None
        prev = all_pages[page_idx - 1] if page_idx > 0 else None
        nxt = all_pages[page_idx + 1] if page_idx < len(all_pages) - 1 else None
        return prev, nxt

    def _render_header(self):
        """Render the sidebar from yaml."""
        st.markdown(f"## {self.header}")

    def _render_navbar(self):
        """Render the sidebar from yaml."""
        for menu in self.navbar:
            if menu.label == "__hidden__":
                continue
            st.markdown(f"### {menu.label}")
            for item in menu.children:
                st.page_link(page=item.filepath, label=item.full_label, use_container_width=True)

    def _render_links(self):
        """Render the sidebar from yaml."""
        html = '<div class="toolbar">'

        html += f'<span role="button" title="Home"><a href="{_BASE_URL}">{_icon("home")}</a></span>'
        if self.links.documentation:
            html += '<span role="button" title="Documentation">'
            html += f'<a href="{self.links.documentation}">{_icon("book_4")}'
            html += "</a></span>"
        if self.links.about:
            html += f'<span role="button" title="About"><a href="{self.links.about}">{_icon("info")}</a></span>'
        if self.links.gethelp:
            html += f'<span role="button" title="Help"><a href="{self.links.gethelp}">{_icon("help")}</a></span>'
        if self.links.bugs:
            html += (
                f'<span role="button" title="Report a Bug"><a href="{self.links.bugs}">{_icon("bug_report")}</a></span>'
            )
        if self.links.settings:
            html += (
                '<span role="button" title="Settings">'
                f'<a href="{self.links.settings}">{_icon("settings")}</a></span>'
            )

        html += "</div>"

        st.html(html)

    def _render_stylesheet(self):
        """Load and apply the stylesheet."""
        with open(DEFAULT_CSS, "r", encoding="UTF-8") as ptr:
            style = ptr.read()
        with st.container(height=1, border=False):
            st.html(f"<style>{style}</style>")

    def sidebar(self):
        """Render the sidebar from yaml."""
        with st.sidebar:
            self._render_header()
            self._render_links()
            self._render_navbar()
            self._render_stylesheet()

    def navigation(self) -> "StreamlitPage":
        """Run the streamlit multipage router."""
        pg = st.navigation(self.page_list)
        return pg

    def footer(self, current: str):
        """Render a footer with prev/next buttons."""
        completed = st.session_state.get(f"{current}_completed")
        total = st.session_state.get(f"{current}_total")
        if completed and total and completed == total:
            # find the next and previous pages
            prev_page, next_page = self.neighbors(current)

            # determine which buttons should be shown
            pills = []
            if prev_page is not None:
                pills.append(PREVIOUS)
            if next_page is not None:
                pills.append(NEXT)

            # render the buttons
            _, right = st.columns([1, 1])
            with right:
                next_steps = st.pills("", pills)

            # handle button presses
            if prev_page and next_steps == PREVIOUS:
                st.switch_page(prev_page)
            elif next_page and next_steps == NEXT:
                st.switch_page(next_page)
