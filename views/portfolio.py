import streamlit as st
import plotly.express as px
import pandas as pd


def create_portfolio_overview(df):
    """Create portfolio overview section"""
    st.header("Portfolio Overview")

    # Ensure 'Invested' column is numeric
    df["Invested"] = pd.to_numeric(
        df["Invested"].astype(str).str.replace(",", "").str.replace(" kr", ""),
        errors="coerce",
    )
    df["Current Value"] = pd.to_numeric(
        df["Current Value"].astype(str).str.replace(",", "").str.replace(" kr", ""),
        errors="coerce",
    )

    # Calculate key metrics
    total_invested = df["Invested"].sum()
    current_value = df["Current Value"].sum()

    # Calculate percentage change with error handling
    if total_invested > 0:
        pct_change = ((current_value - total_invested) / total_invested) * 100
    else:
        pct_change = 0
        st.warning("Total invested amount is 0 or invalid")

    # Display metrics with full values in kronor (no decimals)
    cols = st.columns(3)
    cols[0].metric(
        "Total Invested",
        f"{total_invested:,.0f} kr",
        help="Total amount invested across all holdings",
    )
    cols[1].metric(
        "Current Value",
        f"{current_value:,.0f} kr",
        help="Current market value of all holdings",
    )
    cols[2].metric(
        "Portfolio Change",
        f"{pct_change:+.1f}%",  # Added + sign for positive values
        help="Percentage change from invested amount",
    )

    # Investment source breakdown
    if not df["Source"].empty:
        fig_source = px.pie(
            df,
            values="Invested",
            names="Source",
            title="Investment Source Distribution",
            hole=0.4,  # Makes it a donut chart
        )
        fig_source.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_source, use_container_width=True)

    # Custom color scheme
    company_colors = {
        "SenseHome AB": "#0052CC",  # Dark Blue
        "Sensative AB": "#00B8D9",  # Light Blue
        "LifeFinder AB": "#FF5630",  # Red
        "Currotech AB": "#FF8B00",  # Orange
    }

    # Holdings by company
    company_holdings = df.groupby("Company")["Current Value"].sum().reset_index()
    if not company_holdings.empty:
        fig_holdings = px.pie(
            company_holdings,
            values="Current Value",
            names="Company",
            title="Holdings by Company",
            hole=0.4,  # Makes it a donut chart
            color="Company",
            color_discrete_map=company_colors,
        )
        fig_holdings.update_traces(
            textposition="inside",
            textinfo="percent+label",
            pull=[0.05] * len(company_holdings),  # Slight separation between segments
        )
        st.plotly_chart(fig_holdings, use_container_width=True)

    # Add a data table with key metrics by company
    st.subheader("Company-wise Breakdown")
    company_metrics = (
        df.groupby("Company")
        .agg({"Invested": "sum", "Current Value": "sum", "My Shares": "sum"})
        .reset_index()
    )

    # Calculate company-wise returns
    company_metrics["Return"] = (
        (company_metrics["Current Value"] - company_metrics["Invested"])
        / company_metrics["Invested"]
        * 100
    )

    # Format the columns
    company_metrics["Invested"] = company_metrics["Invested"].apply(
        lambda x: f"{x:,.0f} kr"
    )
    company_metrics["Current Value"] = company_metrics["Current Value"].apply(
        lambda x: f"{x:,.0f} kr"
    )
    company_metrics["My Shares"] = company_metrics["My Shares"].apply(
        lambda x: f"{x:,.0f}"
    )
    company_metrics["Return"] = company_metrics["Return"].apply(lambda x: f"{x:+.1f}%")

    st.dataframe(
        company_metrics,
        column_config={
            "Company": "Company",
            "Invested": "Total Invested",
            "Current Value": "Current Value",
            "My Shares": "Shares Owned",
            "Return": "Return (%)",
        },
        hide_index=True,
    )
