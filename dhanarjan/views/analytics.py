"""Portfolio analytics views."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def calculate_portfolio_concentration(df):
    """Calculate portfolio concentration metrics"""
    total_value = df["Current Value"].sum()

    # Company concentration
    company_concentration = (
        df.groupby("Company")["Current Value"]
        .sum()
        .sort_values(ascending=False)
        .apply(lambda x: (x / total_value) * 100)
    )

    # Source concentration
    source_concentration = (
        df.groupby("Source")["Current Value"]
        .sum()
        .sort_values(ascending=False)
        .apply(lambda x: (x / total_value) * 100)
    )

    return company_concentration, source_concentration


def calculate_wacc(df, loan_df):
    """Calculate Weighted Average Cost of Capital"""
    total_equity = df["Current Value"].sum()
    total_debt = loan_df["Amount"].sum() if loan_df is not None else 0
    total_capital = total_equity + total_debt

    # Cost of debt (weighted average interest rate)
    if loan_df is not None and not loan_df.empty:
        cost_of_debt = (
            (loan_df["Amount"] * loan_df["Interest rate"]).sum() / total_debt
        ) / 100
    else:
        cost_of_debt = 0

    # Assuming cost of equity is 10% (you might want to make this configurable)
    cost_of_equity = 0.10

    # Calculate WACC
    equity_weight = total_equity / total_capital
    debt_weight = total_debt / total_capital

    wacc = (equity_weight * cost_of_equity) + (
        debt_weight * cost_of_debt * 0.78
    )  # Assuming 22% tax rate
    return wacc, equity_weight, debt_weight


def create_portfolio_analytics(df, loan_df):
    """Create portfolio analytics view"""
    st.header("Portfolio Analytics")

    # Calculate metrics
    company_conc, source_conc = calculate_portfolio_concentration(df)
    wacc, equity_weight, debt_weight = calculate_wacc(df, loan_df)

    # Display WACC metrics
    st.subheader("Capital Structure")
    cols = st.columns(4)
    cols[0].metric("WACC", f"{wacc:.2%}")
    cols[1].metric("Equity Weight", f"{equity_weight:.1%}")
    cols[2].metric("Debt Weight", f"{debt_weight:.1%}")
    cols[3].metric("Debt/Equity Ratio", f"{debt_weight/equity_weight:.2f}")

    # Create two columns for concentration charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Company Concentration")
        fig_company = px.pie(
            values=company_conc.values,
            names=company_conc.index,
            title="Portfolio Distribution by Company",
            hole=0.4,
        )
        st.plotly_chart(fig_company, use_container_width=True)

    with col2:
        st.subheader("Source Distribution")
        fig_source = px.pie(
            values=source_conc.values,
            names=source_conc.index,
            title="Investment Distribution by Source",
            hole=0.4,
        )
        st.plotly_chart(fig_source, use_container_width=True)

    # Historical Performance
    st.subheader("Historical Performance")

    # Create timeline of investments and valuations
    timeline_df = df.copy()
    timeline_df["Date"] = pd.to_datetime(timeline_df["Date"])
    timeline_df = timeline_df.sort_values("Date")

    # Calculate cumulative investments and value
    timeline_df["Cumulative Investment"] = timeline_df["Invested"].cumsum()
    timeline_df["Cumulative Value"] = timeline_df["Current Value"].cumsum()

    # Create performance chart
    fig_performance = go.Figure()

    fig_performance.add_trace(
        go.Scatter(
            x=timeline_df["Date"],
            y=timeline_df["Cumulative Investment"],
            name="Total Investment",
            line={"color": "blue"},
        )
    )

    fig_performance.add_trace(
        go.Scatter(
            x=timeline_df["Date"],
            y=timeline_df["Cumulative Value"],
            name="Portfolio Value",
            line={"color": "green"},
        )
    )

    fig_performance.update_layout(
        title="Portfolio Value vs Total Investment",
        xaxis_title="Date",
        yaxis_title="Amount (kr)",
        hovermode="x unified",
    )

    st.plotly_chart(fig_performance, use_container_width=True)
