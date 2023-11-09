import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import sqlite3
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
    return [{'name': info['title'], 'ticker': info['ticker']} for info in ticker_data.values()]

# Load ticker data and get the list of tickers
ticker_data = load_ticker_data()
ticker_list = get_ticker_list(ticker_data)
ticker_dict = {ticker: name for ticker, name in ticker_list}

# Connect to SQLite database
conn = sqlite3.connect('company_info.db')

# Query all records in the table
df = pd.read_sql_query("SELECT * from company_table", conn)

def main():
    st.title("Financial Metrics Analysis")

    # Initialize session state if it doesn't exist
    if 'df_filtered' not in st.session_state:
        st.session_state.df_filtered = df.copy()

    # Filter by Market Cap
    min_market_cap, max_market_cap = st.slider('Market Cap Range', min_value=0, max_value=int(df['Market_Cap'].max()), value=(0, int(df['Market_Cap'].max())))
    # Filter by Revenue
    min_revenue, max_revenue = st.slider('Revenue Range', min_value=0, max_value=int(df['Revenue'].max()), value=(0, int(df['Revenue'].max())))

    # Filter by Region
    regions = st.multiselect('Regions', options=list(df['Country'].unique()), default=[])

    # Filter by Industry
    industries = st.multiselect('Industries', options=list(df['Industry'].unique()), default=[])

    # Filter by Sector
    sector = st.multiselect('Sector', options=list(df['Sector'].unique()), default=[])

    # Sort by metric
    sort_by = st.selectbox('Sort by', options=df.columns)

    # Sort order
    sort_order = st.selectbox('Sort order', options=['Ascending', 'Descending'])

    # Button to apply filters and sort
    if st.button("Apply Filters and Sort"):
        # Filter DataFrame
        df_filtered = df.copy()
        if min_market_cap and max_market_cap:
            df_filtered = df_filtered[(df_filtered['Market_Cap'] >= min_market_cap) & (df_filtered['Market_Cap'] <= max_market_cap)]
        if min_revenue and max_revenue:
            df_filtered = df_filtered[(df_filtered['Revenue'] >= min_revenue) & (df_filtered['Revenue'] <= max_revenue)]
        if regions:
            df_filtered = df_filtered[df_filtered['Country'].isin(regions)]
        if industries:
            df_filtered = df_filtered[df_filtered['Industry'].isin(industries)]
        if sector:
            df_filtered = df_filtered[df_filtered['Sector'].isin(sector)]

        # Sort DataFrame
        if sort_by:
            df_filtered = df_filtered.sort_values(by=sort_by, ascending=(sort_order == 'Ascending'))
        else:
            df_filtered = df_filtered.sort_values(by="Company_Name", ascending=(sort_order == 'Ascending'))

        # Save the filtered DataFrame to session state
        st.session_state.df_filtered = df_filtered

        # Display the DataFrame
        st.dataframe(df_filtered)

    # Get the list of companies from the filtered DataFrame
    companies = [{'name': name, 'ticker': ticker} for name, ticker in zip(st.session_state.df_filtered['Company_Name'].unique(), st.session_state.df_filtered['Symbol'].unique())]

    # Create a multiselect widget for the user to select companies
    selected_companies = st.multiselect(
        'Select Companies',
        options=companies,
        format_func=lambda x: f"{x['name']} ({x['ticker']})"
    )

    # Save the selected companies to the session state
    if selected_companies:
        st.session_state.selected_companies = selected_companies
    else:
        st.session_state.selected_companies = []

    # Create a DataFrame based on the selected companies
    selected_df = st.session_state.df_filtered[st.session_state.df_filtered['Company_Name'].isin([company['name'] for company in st.session_state.selected_companies])]

    # Display the selected DataFrame
    st.dataframe(selected_df)

    # Add a button to continue to the next page
    if st.button("Continue"):
        st.session_state.page = "next"



def next_page():
    # Display the selected companies
    st.header('Selected Companies')
    if 'selected_companies' in st.session_state:
        for company in st.session_state.selected_companies:
            st.write(f"{company['name']} ({company['ticker']})")
    else:
        st.write('No companies selected.')

    # Fetch available metrics for the first company (as a proxy for all companies)
    available_metrics = []
    if st.session_state.selected_companies:
        df_for_metrics = get_dataframes(st.session_state.selected_companies[0]['ticker'])
        available_metrics = get_available_metrics(df_for_metrics.values())

    # Getting user input for metrics using multiselect
    selected_metrics = st.multiselect('Select the financial metrics:', available_metrics)

    # Button to process the data
    if st.button("Fetch Data and Generate Excel"):
        if not st.session_state.selected_companies or not selected_metrics:
            st.error("Please select at least one company and metric.")
            return

        all_data = pd.DataFrame()
        for company in st.session_state.selected_companies:
            dataframes = get_dataframes(company['ticker'])
            metrics_mapping = create_metrics_mapping(dataframes)
            company_data = fetch_selected_metrics(company['ticker'], selected_metrics, dataframes, metrics_mapping)
            all_data = pd.concat([all_data, company_data])

        # Export data to Excel
        file_name = "comparative_analysis.xlsx"
        generate_excel(all_data, file_name)
        st.success(f"Comparative analysis exported to {file_name}!")

        # Optionally, display the data on the app
        st.write(all_data)

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state.page = "main"

    if st.session_state.page == "main":
        main()
    elif st.session_state.page == "next":
        next_page()