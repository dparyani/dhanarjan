"""Advanced visualization views."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_treemap(df):
    """Create treemap visualization of portfolio allocation"""
    # Prepare data for treemap
    treemap_data = (
        df.groupby(["Source", "Company"])
        .agg({"Current Value": "sum", "Invested": "sum"})
        .reset_index()
    )

    fig = px.treemap(
        treemap_data,
        path=[px.Constant("Portfolio"), "Source", "Company"],
        values="Current Value",
        custom_data=["Invested"],
        title="Portfolio Allocation",
        hover_data={"Current Value": ":,.0f kr", "Invested": ":,.0f kr"},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Current Value: %{value:,.0f} kr<br>"
            "Invested: %{customdata[0]:,.0f} kr<br>"
            "<extra></extra>"
        )
    )

    return fig


def create_sankey(df):
    """Create Sankey diagram of money flow"""
    # Prepare data for Sankey
    sources = []
    targets = []
    values = []

    # Create node labels and sort them
    source_names = sorted(df["Source"].unique().tolist())
    company_names = sorted(df["Company"].unique().tolist())
    node_labels = source_names + company_names

    # Create flows from sources to companies
    for i, source in enumerate(source_names):
        source_data = df[df["Source"] == source]
        for company in company_names:
            company_value = source_data[source_data["Company"] == company][
                "Invested"
            ].sum()
            if company_value > 0:
                sources.append(i)
                targets.append(len(source_names) + company_names.index(company))
                values.append(company_value)

    # Create Sankey diagram with improved styling
    fig = go.Figure(
        data=[
            go.Sankey(
                node={
                    "pad": 50,
                    "thickness": 40,
                    "line": {"color": "black", "width": 1},
                    "label": node_labels,
                    "color": ["#1f77b4"] * len(source_names)
                    + ["#2ca02c"] * len(company_names),
                    "hoverlabel": {
                        "bgcolor": "white",
                        "font": {"size": 16, "family": "Arial Black"},
                    },
                    "hovertemplate": "%{label}<br>Amount: %{value:,.0f} kr<extra></extra>",
                },
                link={
                    "source": sources,
                    "target": targets,
                    "value": values,
                    "color": "rgba(169, 169, 169, 0.5)",
                    "hoverlabel": {"bgcolor": "white"},
                    "hovertemplate": (
                        "%{source.label} → %{target.label}<br>"
                        "Amount: %{value:,.0f} kr"
                        "<extra></extra>"
                    ),
                },
            )
        ]
    )

    # Improve layout
    fig.update_layout(
        title={
            "text": "Investment Flow",
            "font": {"size": 24, "family": "Arial Black"},
        },
        font_size=14,
        height=600,
        margin={"t": 60, "b": 40, "l": 40, "r": 40},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    return fig


def create_company_comparison(df):
    """Create comparison charts between companies"""
    # Calculate key metrics per company
    comparison_data = (
        df.groupby("Company")
        .agg({"Invested": "sum", "Current Value": "sum", "My Shares": "sum"})
        .reset_index()
    )

    # Calculate return percentage
    comparison_data["Return"] = (
        (comparison_data["Current Value"] - comparison_data["Invested"])
        / comparison_data["Invested"]
        * 100
    )

    # Create comparison bar chart
    fig = go.Figure()

    # Add bars for invested amount
    fig.add_trace(
        go.Bar(
            name="Invested",
            x=comparison_data["Company"],
            y=comparison_data["Invested"],
            marker_color="blue",
        )
    )

    # Add bars for current value
    fig.add_trace(
        go.Bar(
            name="Current Value",
            x=comparison_data["Company"],
            y=comparison_data["Current Value"],
            marker_color="green",
        )
    )

    # Add return percentage as a line
    fig.add_trace(
        go.Scatter(
            name="Return %",
            x=comparison_data["Company"],
            y=comparison_data["Return"],
            yaxis="y2",
            line={"color": "red", "width": 2},
            mode="lines+markers",
        )
    )

    fig.update_layout(
        title="Company Performance Comparison",
        yaxis={"title": "Amount (kr)"},
        yaxis2={
            "title": "Return %",
            "overlaying": "y",
            "side": "right",
            "tickformat": ".1f",
        },
        barmode="group",
        hovermode="x unified",
    )

    return fig


def create_visualizations(df):
    """Create advanced visualizations view"""
    st.header("Advanced Visualizations")

    # Date range filter
    st.subheader("Date Range Filter")
    st.info("Filter all visualizations below by selecting a date range")

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            min_value=df["Date"].min(),
            max_value=df["Date"].max(),
            value=df["Date"].min(),
            help="Select the starting date for the analysis period",
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            min_value=df["Date"].min(),
            max_value=df["Date"].max(),
            value=df["Date"].max(),
            help="Select the ending date for the analysis period",
        )

    # Filter data based on date range
    mask = (df["Date"] >= pd.Timestamp(start_date)) & (
        df["Date"] <= pd.Timestamp(end_date)
    )
    filtered_df = df[mask]

    # Show treemap
    st.subheader("Portfolio Allocation (Treemap)")
    st.info(
        "Hierarchical view of your portfolio showing how investments are distributed "
        "across different sources and companies. Size represents current value."
    )
    st.plotly_chart(create_treemap(filtered_df), use_container_width=True)

    # Show Sankey diagram
    st.subheader("Investment Flow (Sankey)")
    st.info(
        "Visual representation of money flow from different sources to companies. "
        "Thickness of lines represents investment amount."
    )
    st.plotly_chart(create_sankey(filtered_df), use_container_width=True)

    # Calculate metrics for display
    metrics_data = (
        df.groupby("Company")
        .agg({"Invested": "sum", "Current Value": "sum", "My Shares": "sum"})
        .reset_index()
    )

    total_invested = metrics_data["Invested"].sum()
    total_value = metrics_data["Current Value"].sum()
    total_shares = metrics_data["My Shares"].sum()
    pct_change = ((total_value - total_invested) / total_invested) * 100

    # Show company comparison
    st.subheader("Company Performance Comparison")
    st.info(
        "Side-by-side comparison of companies showing invested amount, current value, "
        "and return percentage. Bars show amounts, line shows returns."
    )
    st.plotly_chart(create_company_comparison(filtered_df), use_container_width=True)

    # Add metrics with tooltips
    cols = st.columns(5)
    cols[0].metric(
        "Total Invested",
        f"{total_invested:,.0f} kr",
        help="Total amount invested across all companies",
    )
    cols[1].metric(
        "Current Value",
        f"{total_value:,.0f} kr",
        help="Current market value of all investments",
    )
    cols[2].metric(
        "Portfolio Change",
        f"{pct_change:+.1f}%",
        help="Overall portfolio return percentage",
    )
    cols[3].metric(
        "Total Shares",
        f"{total_shares:,}",
        help="Total number of shares across all companies",
    )
    cols[4].metric(
        "Average Return",
        f"{pct_change:.2f}%",
        help="Average return across all investments",
    )
