"""
Entry and client authentication page
"""
from os import environ
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from portfolio_mgmt.client.client import Client
from portfolio_mgmt.utils.exceptions import BadCredentials

def _authenticate(client, username, password, totp):
    try:
        client.login(username, password, totp)
        st.success("Login successful")
    except BadCredentials as e:
        st.error("**Login failed:** Wrong credentials or an expired 2FA token was passed")

def _new_client():
    client = Client()

    load_dotenv()

    login_form = st.empty()

    with login_form.form(key="Login"):
        st.markdown("#### Enter your credentials and 2FA token:")
        username = st.text_input("Username:", value=environ.get("DG_USERNAME"))
        password = st.text_input("Password:", value=environ.get("DG_PASSWORD"), type="password")
        totp = st.text_input("2FA Token:")
        button = st.form_submit_button("Login")

    if button:
        _authenticate(client, username, password, totp)
        if client._authenticated:
            login_form.empty()
            st.session_state["auth_client"] = client
            return client

def get_client() -> Optional[Client]:
    client = st.session_state.get("auth_client", default=None)
    if not client and __name__=='__main__':
        client = _new_client()
    return client

client = get_client()

if __name__=='__main__' and client:
    st.write(f"Welcome *{client._user}* 👋")