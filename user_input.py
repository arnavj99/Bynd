def get_user_inputs(tickers, available_metrics):
    st.sidebar.header('User Input')
    tickers = st.sidebar.text_input("Enter the company tickers (comma separated):")
    tickers = [ticker.strip() for ticker in tickers.split(',')]  # Cleaning up the tickers
    selected_metrics = st.sidebar.multiselect('Select the financial metrics:', available_metrics)
    return tickers, selected_metrics

def validate_input(tickers, selected_metrics):
    if not tickers or not selected_metrics:
        st.error('Please enter both tickers and select at least one metric.')
        return False
    return True
