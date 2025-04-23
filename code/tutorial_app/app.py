"""Top level streamlit app page."""

from pathlib import Path

import live_labs

# Load the page data
app_shell_yaml = Path(__file__).parent.joinpath("pages", "sidebar.yaml")
app = live_labs.AppShell.from_yaml(app_shell_yaml)

# Render the default app shell
page = app.navigation()
app.sidebar()
page.run()
