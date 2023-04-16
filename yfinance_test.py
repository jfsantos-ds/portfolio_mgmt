from yahooquery import Ticker

tcks = Ticker(['aapl','msft'], validate=True)

#tcks.summary_detail

#print(tcks)

data = tcks.asset_profile

data2 = tcks.history(period='1y')

tcks2 = Ticker('aaasswq', validate=True)

#print(tcks2)

import plotly.graph_objects as go

import pandas as pd

fig = go.Figure(data=go.Ohlc(x=data2.loc['MSFT'].index.values,
                    open=data2.loc['MSFT']['open'],
                    high=data2.loc['MSFT']['high'],
                    low=data2.loc['MSFT']['low'],
                    close=data2.loc['MSFT']['close']))

#fig.show()

import streamlit as st

st.plotly_chart(fig, use_container_width=True)