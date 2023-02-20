"""
Explore products page.
"""
from datetime import date

import plotly.graph_objects as go
import streamlit as st
import yahooquery as yq

from portfolio_mgmt.utils.globals import DEFAULT_START_DATE

SUPPORTED_PRODUCTS = ["EQUITY", "ETF"]


@st.cache
def search_supported_tickers(search_name):
    data = yq.search(search_name, news_count=0)["quotes"]
    found_tickers = filter(lambda x: x["quoteType"] in SUPPORTED_PRODUCTS, data)
    return {ticker["symbol"]: ticker for ticker in found_tickers}


@st.cache
def get_ticker(symbol):
    return yq.Ticker(symbol, validate=True)


@st.cache
def get_history(ticker, start, symbol):
    return ticker.history(start=start).loc[symbol]


st.header("Explore products")
search_name = st.text_input("Input a ticker symbol or company name")

if search_name:
    found_tickers = search_supported_tickers(search_name)
    st.markdown(f"Found **{len(found_tickers)}** results based on your search.\nSelect one from the list:")
    symbol = st.selectbox("Select ticker symbol", options=list(found_tickers.keys()))

    if symbol:
        selected_ticker = get_ticker(symbol)
        st.markdown("#### Define ticker history start point")
        start = st.date_input("**From**", date(*DEFAULT_START_DATE), max_value=date.today())
        end = date.today()

        st.header(f"{found_tickers[symbol]['shortname']}")

        history = get_history(selected_ticker, start, symbol)

        fig = go.Figure(
            data=go.Ohlc(
                x=history.index.values,
                open=history["open"],
                high=history["high"],
                low=history["low"],
                close=history["close"],
            )
        )

        st.plotly_chart(fig, use_container_width=True)
