"""
Explore products page.
"""
from datetime import date

import plotly.graph_objects as go
import streamlit as st
import yahooquery as yq

from portfolio_mgmt.utils.globals import COUNTRY_MAPPER, DEFAULT_START_DATE

SUPPORTED_PRODUCTS = ["EQUITY", "ETF"]


@st.cache_data
def search_supported_tickers(search_name):
    data = yq.search(search_name, news_count=0)["quotes"]
    found_tickers = filter(lambda x: x["quoteType"] in SUPPORTED_PRODUCTS, data)
    return {ticker["symbol"]: ticker for ticker in found_tickers}


@st.cache_resource
def get_ticker(symbol):
    return yq.Ticker(symbol, validate=True)


@st.cache_data
def get_history(_ticker, symbol, start):
    return _ticker.history(start=start).loc[symbol]


@st.cache_data
def get_asset_profile(_ticker, symbol):
    return _ticker.asset_profile[symbol]


def structure_profile(asset_profile):
    c1, c2 = st.columns(2)

    c1.markdown("**Sector**")
    c2.markdown(asset_profile.get("sector"))

    c1.markdown("**Industry**")
    c2.markdown(asset_profile.get("industry"))

    country = asset_profile.get("country")
    c1.markdown("**Country**")
    if country_short := COUNTRY_MAPPER.get(country):
        c2.markdown(f":flag-{country_short}:")
    else:
        c2.markdown(country)

    c1.markdown("**Main address**")
    c2.markdown(
        ", ".join(
            [
                e
                for e in [
                    asset_profile.get("address1"),
                    asset_profile.get("zip"),
                    asset_profile.get("city"),
                    asset_profile.get("state"),
                ]
                if e
            ]
        )
    )

    c1.markdown("**Permanent employees**")
    c2.markdown(asset_profile.get("fullTimeEmployees", "Not available"))

    c1.markdown("**Website**")
    if website := asset_profile.get("website"):
        c2.markdown(f"[{website}](%s)" % website)
    else:
        c2.markdown("Not available")

    c1.markdown("**Business description**")
    c2.markdown(asset_profile.get("longBusinessSummary"))


st.header("Explore products")

symbol = None

with st.expander("Product search:", expanded=True):
    search_name = st.text_input("Input a ticker symbol or company name")

    if search_name:
        found_tickers = search_supported_tickers(search_name)
        if len(found_tickers) > 1:
            symbol = st.selectbox(
                "Not what you were looking for? Here are the most relevant hits:", options=list(found_tickers.keys())
            )
        elif len(found_tickers) == 1:
            symbol = list(found_tickers.keys())[0]
        else:
            st.markdown("No symbol was found:disappointed: Try a new search?")

if symbol:
    shortname = found_tickers[symbol]["shortname"]
    ticker = get_ticker(symbol)
    st.header(f"{shortname}")

    tab1, tab2 = st.tabs(["Overview", "Price chart"])

    with tab1:
        asset_profile = get_asset_profile(ticker, symbol)

        with st.container():
            structure_profile(asset_profile)

    with tab2:
        st.markdown("#### Define ticker history start point")
        start = st.date_input("**From**", date(*DEFAULT_START_DATE), max_value=date.today())
        end = date.today()

        history = get_history(ticker, symbol, start)

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
