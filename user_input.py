def get_user_inputs(tickers, available_metrics):
    # Print the available metrics
    print(f'Available Metrics: {", ".join(available_metrics)}')

    # Get the metrics from the user
    selected_metrics_input = input("Enter the financial metrics (comma separated): ")
    selected_metrics = [metric.strip() for metric in selected_metrics_input.split(',')]  # Cleaning up the metrics

    return selected_metrics

def validate_input(tickers, selected_metrics):
    if not tickers or not selected_metrics:
        print('Error: Please enter both tickers and select at least one metric.')
        return False
    return True