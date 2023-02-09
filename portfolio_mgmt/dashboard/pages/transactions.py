"""
Transactions app.
"""
from datetime import date

import streamlit as st

from portfolio_mgmt.dashboard.login import get_client
from portfolio_mgmt.utils.globals import DEFAULT_START_DATE
from portfolio_mgmt.utils.style import transactions_styler

client = get_client()

@st.cache
def get_all_transactions(client, start, end, styler_fn: lambda x: x):
    transactions = client.get_transactions(start, end)
    return transactions.style.pipe(styler_fn)

if client:
    tab1, tab2 = st.tabs(["All products", "Single product"])

    with tab1:
        st.header("Transaction history")
        st.markdown("### Define a time window")
        col1, col2 = st.columns(2)
        with col1:
            start = st.date_input(
                "**From**",
                date(*DEFAULT_START_DATE),
                max_value=date.today()
                )
        with col2:
            end = st.date_input(
                "**To** (Defaults to today)",
                date.today(),
                min_value=start,
                )

        transactions = get_all_transactions(client, start, end, transactions_styler)

        st.write(f"**{len(transactions)}** total transactions within this period:")
        st.dataframe(transactions, use_container_width=True)

    products = sorted(list(transactions.name.unique()), key=str.casefold)

    with tab2:
        st.header("Single product transactions")
        st.write("From", start, "to", end, "(adjust time window in *All products* tab)")
        product_name = st.selectbox("Select product", options=products)
        product_transactions = transactions.loc[transactions.name == product_name]
        ticker = product_transactions.symbol.values[0]
        st.write(f"**{len(product_transactions)} {ticker}** transactions within this period:")
        st.write(product_transactions)
