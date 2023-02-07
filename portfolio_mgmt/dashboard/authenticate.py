"""
Get an authenticated client
"""
from os import environ

from dotenv import load_dotenv
import streamlit as st

from portfolio_mgmt.client.client import Client
from portfolio_mgmt.utils.exceptions import BadCredentials

def get_client():
    if (client:=st.session_state.get("auth_client")):
        return client
    
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
        try:
            client.login(username, password, totp)
            if client._authenticated:
                login_form.empty()
                st.success("Login successful")
                st.session_state["auth_client"] = client
        except BadCredentials as e:
            st.error("**Login failed:** Wrong credentials or an expired 2FA token was passed")
    return client
