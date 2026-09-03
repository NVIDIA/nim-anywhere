# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Fail-closed authentication gate for Live Labs Streamlit applications."""

import os
import secrets
import time

import streamlit as st

API_KEY_ENV = "NIM_ANYWHERE_API_KEY"
MINIMUM_API_KEY_LENGTH = 32
_AUTHENTICATED_STATE_KEY = "_nim_anywhere_authenticated"
_PASSWORD_INPUT_KEY = "_nim_anywhere_password"


def require_authentication() -> None:
    """Stop rendering the app until the user proves knowledge of its API key."""
    if st.session_state.get(_AUTHENTICATED_STATE_KEY, False):
        return

    api_key = os.environ.get(API_KEY_ENV, "")
    if len(api_key) < MINIMUM_API_KEY_LENGTH:
        st.error(f"Authentication is not configured. Set {API_KEY_ENV} to at least 32 characters.")
        st.stop()

    st.title("NIM Anywhere authentication")
    with st.form("nim-anywhere-login", clear_on_submit=True):
        supplied_key = st.text_input("API key", type="password", key=_PASSWORD_INPUT_KEY)
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if secrets.compare_digest(supplied_key, api_key):
            st.session_state[_AUTHENTICATED_STATE_KEY] = True
            st.session_state.pop(_PASSWORD_INPUT_KEY, None)
            st.rerun()
        time.sleep(0.5)
        st.error("Invalid API key.")

    st.stop()
