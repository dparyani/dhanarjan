"""

Company performance views.

This module contains views for displaying company performance metrics and charts.

It includes functions for creating line charts of price history and pie charts of ownership distribution.

"""

from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st


def create_company_performance(df, total_shares_df):
    """Create company performance section"""
    st.header("Company Performance")

    # Company selector
    selected_company = st.selectbox("Select Company", df["Company"].unique())

    company_data = df[df["Company"] == selected_company]
    total_shares = total_shares_df[total_shares_df["Company"] == selected_company][
        "Total Shares"
    ].iloc[0]

    # Calculate metrics
    total_invested = company_data["Invested"].sum()
    current_value = company_data["Current Value"].sum()
    my_shares = company_data["My Shares"].sum()
    ownership_pct = (my_shares / total_shares) * 100
    return_pct = ((current_value - total_invested) / total_invested) * 100

    # Display metrics
    cols = st.columns(5)
    cols[0].metric("Total Invested", f"{total_invested:,.0f} kr")
    cols[1].metric("Current Value", f"{current_value:,.0f} kr")
    cols[2].metric("Return", f"{return_pct:+.1f}%")
    cols[3].metric("My Shares", f"{my_shares:,}")
    cols[4].metric("Ownership", f"{ownership_pct:.2f}%")

    # Create a date range from first investment to today
    start_date = company_data["Date"].min()
    end_date = datetime.now()
    date_range = pd.date_range(start=start_date, end=end_date, freq="ME")

    # Create a DataFrame with the full date range
    timeline_df = pd.DataFrame(date_range, columns=["Date"])

    # Get the latest price for the company
    current_price = company_data["Current Market Price"].iloc[-1]

    # Merge with actual investment data
    timeline_df = pd.merge(
        timeline_df, company_data[["Date", "Price Paid"]], on="Date", how="left"
    )

    # Fill in the current market price for all dates
    timeline_df["Current Market Price"] = current_price

    # Forward fill the Price Paid using ffill()
    timeline_df["Price Paid"] = timeline_df["Price Paid"].ffill()

    # Investment timeline with actual prices
    fig_timeline = px.line(
        timeline_df,
        x="Date",
        y=["Price Paid", "Current Market Price"],
        title=f"{selected_company} - Price History",
        labels={"value": "Price (kr)", "variable": "Price Type"},
    )

    # Update line names and styling
    fig_timeline.data[0].name = "Price Paid"
    fig_timeline.data[1].name = "Current Market Price"

    # Add markers for actual investment dates
    fig_timeline.add_scatter(
        x=company_data["Date"],
        y=company_data["Price Paid"],
        mode="markers",
        name="Investment Points",
        marker={"size": 10, "symbol": "circle"},
        hovertemplate="Date: %{x}<br>Price: %{y:,.2f} kr<extra></extra>",
    )

    # Improve layout
    fig_timeline.update_layout(
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Price (kr)",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )

    st.plotly_chart(fig_timeline, use_container_width=True)
