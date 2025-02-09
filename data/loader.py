"""
Data loading functions.

This module contains functions for loading data from Google Sheets.

The data is loaded from a Google Sheet that contains the following sheets:
- Investment
- Total Shares
- Loans

"""

import streamlit as st
import pandas as pd
from utils.google_auth import get_google_sheets_service
from config import SPREADSHEET_ID, SHEET_NAME


@st.cache_data
def load_data():
    """Load investment data from Google Sheets"""
    try:
        service = get_google_sheets_service()

        # Load the entire sheet
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME)
            .execute()
        )

        values = result.get("values", [])
        if not values:
            st.error("No data found in the sheet.")
            return None, None, None

        # Process investment data (columns 0-9)
        investment_columns = values[0][:10]  # First 10 columns
        investment_data = [
            row[:10] for row in values[1:] if len(row) > 9
        ]  # Skip empty rows
        df = pd.DataFrame(investment_data, columns=investment_columns)

        # Process total shares data (columns 11-13)
        shares_columns = ["Company", "Org.No.", "Total Shares"]
        shares_data = [
            [row[11], row[12], row[13]]
            for row in values[1:]
            if len(row) > 13 and row[11]
        ]
        total_shares_df = pd.DataFrame(shares_data, columns=shares_columns)

        # Process loans data (columns 15-17)
        loans_columns = ["Loans", "Interest rate", "Amount"]
        loans_data = [
            [row[15], row[16], row[17]]
            for row in values[1:]
            if len(row) > 17 and row[15]
        ]
        loans_df = pd.DataFrame(loans_data, columns=loans_columns)

        # Convert currency columns in investment data
        def convert_currency(value):
            if isinstance(value, str):
                # Remove 'kr' and spaces, replace comma with dot
                value = value.replace(" kr", "").replace(",", "").strip()
                try:
                    return float(value)
                except ValueError:
                    return 0.0
            return float(value) if value else 0.0

        currency_columns = [
            "Price Paid",
            "Invested",
            "Current Market Price",
            "Current Value",
        ]
        for col in currency_columns:
            if col in df.columns:
                df[col] = df[col].apply(convert_currency)

        # Convert numeric columns in investment data
        numeric_columns = ["No.", "My Shares"]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Convert date column
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y")

        # Convert Total Shares to numeric
        if "Total Shares" in total_shares_df.columns:
            total_shares_df["Total Shares"] = pd.to_numeric(
                total_shares_df["Total Shares"], errors="coerce"
            )

        # Convert Amount to numeric in loans data
        if "Amount" in loans_df.columns:
            loans_df["Amount"] = loans_df["Amount"].apply(convert_currency)

        # Convert Interest rate to numeric
        if "Interest rate" in loans_df.columns:

            def clean_interest_rate(rate):
                if isinstance(rate, str):
                    rate = rate.rstrip("%")
                    try:
                        return float(rate)
                    except ValueError:
                        return 0.0
                return float(rate) if rate else 0.0

            loans_df["Interest rate"] = loans_df["Interest rate"].apply(
                clean_interest_rate
            )

        return df, total_shares_df, loans_df

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Exception details:", e)
        return None, None, None
