import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import streamlit as st
import json
from init_setup import setup_openbb_key
from data_retrieval import get_dataframes
from data_processing_and_export import get_available_metrics, create_metrics_mapping, fetch_selected_metrics, generate_excel

# Set up the openBB API key
setup_openbb_key()

# Load the JSON file containing the tickers
@st.cache_resource
def load_ticker_data():
    with open('company_tickers.json', 'r') as f:
        return json.load(f)

# Extract ticker symbols and names for the search bar
def get_ticker_list(ticker_data):
    return [(info['ticker'], info['title']) for info in ticker_data.values()]

# Load ticker data and get the list of tickers
ticker_data = load_ticker_data()
ticker_list = get_ticker_list(ticker_data)
ticker_dict = {ticker: name for ticker, name in ticker_list}

def main():
    st.title("Financial Metrics Analysis")

    # Sidebar - Ticker selection
    st.sidebar.header('Ticker Selection')
    selected_tickers = st.sidebar.multiselect(
        'Select ticker(s)',
        options=ticker_dict.keys(),
        format_func=lambda x: f"{ticker_dict[x]} ({x})",
        help='Start typing to search for a ticker symbol'
    )

    # Sidebar - Metric selection
    st.sidebar.header('Metric Selection')
    # Fetch available metrics for the first ticker (as a proxy for all tickers)
    available_metrics = []
    if selected_tickers:
        df_for_metrics = get_dataframes(selected_tickers[0])
        available_metrics = get_available_metrics(df_for_metrics.values())

    # Getting user input for metrics using multiselect
    selected_metrics = st.sidebar.multiselect('Select the financial metrics:', available_metrics)

    # Button to process the data
    if st.button("Fetch Data and Generate Excel"):
        if not selected_tickers or not selected_metrics:
            st.error("Please select at least one ticker and metric.")
            return

        all_data = pd.DataFrame()
        for ticker in selected_tickers:
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
