import streamlit as st
import plotly.graph_objects as go


def create_investment_timeline(df):
    """Create investment timeline section"""
    st.header("Investment Timeline")

    # Cumulative investment over time
    df_sorted = df.sort_values("Date")
    df_sorted["Cumulative Investment"] = df_sorted["Invested"].cumsum()
    df_sorted["Cumulative Value"] = df_sorted["Current Value"].cumsum()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_sorted["Date"],
            y=df_sorted["Cumulative Investment"],
            name="Total Investment",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_sorted["Date"], y=df_sorted["Cumulative Value"], name="Current Value"
        )
    )
    fig.update_layout(title="Portfolio Growth Over Time")
    st.plotly_chart(fig, use_container_width=True)
