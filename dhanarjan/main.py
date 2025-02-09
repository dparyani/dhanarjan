"""

Main application file.

This file contains the main application logic for the Start-ups Investment Portfolio Dashboard.

It sets up the Streamlit interface and loads the necessary data from the Google Sheets.

"""

import streamlit as st
from dhanarjan.data.loader import load_data
from dhanarjan.views.portfolio import create_portfolio_overview
from dhanarjan.views.company import create_company_performance
from dhanarjan.views.timeline import create_investment_timeline
from dhanarjan.views.loans import create_loan_analysis
from dhanarjan.views.analytics import create_portfolio_analytics


def main():
    st.set_page_config(
        page_title="Dhanarjan - Investment Portfolio", page_icon="📈", layout="wide"
    )

    # Custom title with inline styles
    st.markdown(
        """
        <h1 style="
            color: #C0C0C0;
            font-size: 72px !important;
            font-family: 'Source Sans Pro', sans-serif;
            margin: 0;
            padding: 0;
            font-weight: 700;
            line-height: 1;
        ">Dhanarjan</h1>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Start-ups Investment Portfolio Dashboard")

    # Load all data at once
    df, total_shares_df, loan_df = load_data()
    if df is None or total_shares_df is None or loan_df is None:
        st.error("Failed to load data. Please check the error messages above.")
        return

    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Portfolio Overview",
            "Portfolio Analytics",
            "Company Performance",
            "Investment Timeline",
            "Loan Analysis",
        ]
    )

    with tab1:
        create_portfolio_overview(df)

    with tab2:
        create_portfolio_analytics(df, loan_df)

    with tab3:
        create_company_performance(df, total_shares_df)

    with tab4:
        create_investment_timeline(df)

    with tab5:
        create_loan_analysis(loan_df)

    # Display raw data
    if st.checkbox("Show Raw Data"):
        st.dataframe(df)


if __name__ == "__main__":
    main()
