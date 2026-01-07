"""
AuthX Streamlit UI

Reusable Streamlit UI helpers built on top of AuthX core services.
"""

import streamlit as st
from typing import Dict, Any

from authx.core.services import AuthService, LicenseService
from authx.integrations.sqlite_storage import SQLiteAuthStorage
from config import AppConfig

class AuthX:
    def __init__(self):
        storage = SQLiteAuthStorage()
        self.auth = AuthService(storage, session_timeout_hours=AppConfig.get_auth_settings().get('session_timeout_hours', 24))
        self.license = LicenseService(storage, plans=AppConfig.get_auth_settings().get('license_plans', {}))

    def gate(self) -> bool:
        if not st.session_state.get('ENABLE_AUTHENTICATION', False):
            return True
        token = st.session_state.get('session_token')
        if token:
            user = self.auth.get_current_user(token)
            if user:
                st.session_state['current_user'] = user
                valid, _, _ = self.license.validate(user['id'])
                if not valid:
                    st.warning("Please activate your license to continue")
                    return False
                return True
            else:
                st.session_state.pop('session_token', None)
        return False

    def login_form(self):
        with st.form("authx_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                ok, msg, user = self.auth.login(email, password)
                if ok and user:
                    st.session_state['session_token'] = user['session_token']
                    st.success("Logged in")
                    st.rerun()
                else:
                    st.error(msg)

    def register_form(self):
        with st.form("authx_register"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Register")
            if submit:
                ok, msg = self.auth.register_user(username, email, password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
