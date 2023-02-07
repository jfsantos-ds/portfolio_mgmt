"""
Transactions app.
"""

from datetime import datetime as dt

import streamlit as st

from portfolio_mgmt.dashboard.authenticate import get_client

client = get_client()


@st.cache
def get_all_transactions(client, start):
    return client.get_transactions(start)


if client._authenticated:
    st.write(f"Welcome *{client._user}* 👋")

    start = dt(2019, 1, 1)

    transactions = get_all_transactions(client, start)

    st.write("Visualize transactions:")
    st.write(transactions)

    products = sorted(list(transactions.name.unique()), key=str.casefold)

    stock_name = st.selectbox("Select a single product", options=products)

    st.write(transactions.loc[transactions.name == stock_name])
