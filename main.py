from init_setup import setup_openbb_key
from data_retrieval import get_dataframes
from user_input import get_user_inputs, validate_input
from data_processing_export import get_available_metrics, create_metrics_mapping, fetch_selected_metrics, generate_excel

def main():
    setup_openbb_key()
    # Get the tickers from the user
    tickers_input = input("Enter the company tickers (comma separated): ")
    tickers = [ticker.strip() for ticker in tickers_input.split(',')]  # Cleaning up the tickers

    # Get the dataframes for the tickers
    all_dataframes = {ticker: get_dataframes(ticker) for ticker in tickers}

    # Get the available metrics from the dataframe of the first ticker
    available_metrics = get_available_metrics(next(iter(all_dataframes.values())).values())

    # Get user inputs for metrics
    selected_metrics = get_user_inputs(tickers, available_metrics)
    # Validate the input
    if not validate_input(tickers, selected_metrics):
        return

    # Fetch the selected metrics for each ticker
    all_data_local = pd.DataFrame()
    for ticker in tickers:
        dataframes = all_dataframes[ticker]
        metrics_mapping = create_metrics_mapping(dataframes)
        ticker_data = fetch_selected_metrics(ticker, selected_metrics, dataframes, metrics_mapping)
        all_data_local = pd.concat([all_data_local, ticker_data])
        generate_excel(all_data_local)
    print(all_data_local)
    print('Comparative analysis exported to comparative_analysis.xlsx')
# Running the main function when the script is executed

if __name__ == "__main__":
    main()
