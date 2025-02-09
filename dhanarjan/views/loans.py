import streamlit as st
import plotly.express as px


def create_loan_analysis(df):
    """Create loan analysis section"""
    st.header("Loan Analysis")

    if df is None or df.empty:
        st.warning("No loan data available")
        return

    # Calculate total loan amount
    total_loans = df["Amount"].sum()
    st.metric("Total Loans", f"{total_loans:,.0f} kr")

    # Create pie chart for loan distribution
    fig_loans = px.pie(
        df,
        values="Amount",
        names="Loans",  # Using 'Loans' column
        title="Loan Distribution",
        hole=0.4,
    )
    fig_loans.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_loans, use_container_width=True)

    # Display loan details in a table
    st.subheader("Loan Details")

    # Format the display data
    display_df = df.copy()
    display_df["Amount"] = display_df["Amount"].apply(lambda x: f"{x:,.0f} kr")
    display_df["Interest rate"] = display_df["Interest rate"].apply(
        lambda x: f"{x:.2f}%"
    )

    st.dataframe(display_df, hide_index=True)

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        # Display loan breakdown
        st.subheader("Loan Breakdown")

        # Create a pie chart of loans using 'Loans' column
        fig_loans = px.pie(
            df,
            values="Amount",
            names="Loans",  # Using 'Loans' column
            title="Loan Distribution",
        )
        st.plotly_chart(fig_loans, use_container_width=True)

    with col2:
        # Display repayment strategy
        st.subheader("Recommended Repayment Strategy")

        # Sort loans by interest rate (highest to lowest)
        strategy_df = df.sort_values("Interest rate", ascending=False).copy()

        # Calculate monthly interest cost
        strategy_df["Monthly Interest Cost"] = (
            strategy_df["Amount"] * (strategy_df["Interest rate"] / 100) / 12
        )

        # Create a table with the strategy
        strategy_table = strategy_df.copy()
        strategy_table["Priority"] = range(1, len(strategy_table) + 1)
        strategy_table["Interest rate"] = strategy_table["Interest rate"].map(
            lambda x: f"{x:.2f}%"
        )
        strategy_table["Amount"] = strategy_table["Amount"].map(
            lambda x: f"{x:,.0f} kr"
        )
        strategy_table["Monthly Interest Cost"] = strategy_table[
            "Monthly Interest Cost"
        ].map(lambda x: f"{x:,.0f} kr")

        st.write("Repayment Priority (Debt Avalanche Method):")
        st.table(
            strategy_table[
                [
                    "Priority",
                    "Loans",
                    "Interest rate",
                    "Amount",
                    "Monthly Interest Cost",
                ]
            ]
        )

        # Calculate and display total monthly interest
        total_monthly_interest = (df["Amount"] * (df["Interest rate"] / 100) / 12).sum()
        st.metric("Total Monthly Interest Cost", f"{total_monthly_interest:,.0f} kr")
