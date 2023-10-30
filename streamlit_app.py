import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import streamlit as st
from init_setup import setup_openbb_key
from data_retrieval import get_dataframes
from data_processing_and_export import get_available_metrics, create_metrics_mapping, fetch_selected_metrics, generate_excel

# Set up the openBB API key
setup_openbb_key()

def main():
    st.title("Financial Metrics Analysis")

    # Getting user input for tickers
    tickers_input = st.text_input("Enter the company tickers (comma separated):")
    tickers = [ticker.strip() for ticker in tickers_input.split(',')] if tickers_input else []

    # Fetch available metrics for the first ticker (as a proxy for all tickers)
    # Assuming here that the available metrics will be same for all tickers
    sample_ticker = tickers[0] if tickers else None
    available_metrics = []
    if sample_ticker:
        df_for_metrics = get_dataframes(sample_ticker)
        available_metrics = get_available_metrics(df_for_metrics.values())

    # Getting user input for metrics using multiselect
    selected_metrics = st.multiselect('Select the financial metrics:', available_metrics)

    # Button to process the data
    if st.button("Fetch Data and Generate Excel"):
        if not tickers or not selected_metrics:
            st.error("Please provide both tickers and select at least one metric.")
            return

        all_data = pd.DataFrame()
        for ticker in tickers:
            dataframes = get_dataframes(ticker)
            metrics_mapping = create_metrics_mapping(dataframes)
            ticker_data = fetch_selected_metrics(ticker, selected_metrics, dataframes, metrics_mapping)
            all_data = pd.concat([all_data, ticker_data])

        # Export data to Excel
        file_name = "comparative_analysis.xlsx"
        generate_excel(all_data, file_name)
        st.success(f"Comparative analysis exported to {file_name}!")

        # Optionally, display the data on the app
        st.write(all_data)

if __name__ == "__main__":
    main()
