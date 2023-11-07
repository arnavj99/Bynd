import pandas as pd

def get_available_metrics(dataframes):
    metrics = set()
    for df in dataframes:
        # This print statement is for debugging purposes
        print(f"Currently processing: {df}, Type: {type(df)}")
        # Ensure that df is a pandas DataFrame or Series
        if isinstance(df, (pd.DataFrame, pd.Series)):
            metrics.update(df.index.tolist())
        else:
            print(f"Error: Object {df} is not a pandas DataFrame or Series.")
    return list(metrics)

def create_metrics_mapping(dataframes):
    metrics_mapping = {}
    for df_name, df in dataframes.items():
        for metric in df.index:
            metrics_mapping[metric] = df_name
    return metrics_mapping

def fetch_selected_metrics(ticker, selected_metrics, dataframes, metrics_mapping):
    data = pd.DataFrame(index=[ticker], columns=selected_metrics)  # Initialize DataFrame with ticker as index and metrics as columns
    for metric in selected_metrics:
        df_name = metrics_mapping[metric]
        df = dataframes[df_name]
        value = df.loc[metric].values[0]
        # Check if the value is a number and greater than 1000
        if isinstance(value, (int, float)) and value > 100000:
            value /= 1e6  # Convert to millions
        elif isinstance(value, str):  # Check if the value is a string
            try:
                value = float(value)  # Try converting the string to a float
                if value > 100000:
                  value /= 1e6  # Convert to millions
            except ValueError:
                pass  # Ignore if the string cannot be converted to a float
        data.loc[ticker, metric] = value  # Assume the most recent data is needed
    return data

def generate_excel(data, file_name='comparative_analysis.xlsx'):
    # Export DataFrame to Excel File
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        data.to_excel(writer)
        for column in data.columns:
            numeric_data = pd.to_numeric(data[column], errors='coerce').dropna()
            if (numeric_data <= 1).all():  # Check if all values in the column are less than or equal to 1
                col_num = data.columns.get_loc(column) + 1  # +1 because Excel uses 1-indexing
                for row_num in range(2, len(data) + 2):  # +2 because Excel uses 1-indexing and there's a header row
                    cell = writer.sheets['Sheet1'].cell(row=row_num, column=col_num)
                    cell.number_format = '0.00%'
    print(f'Data exported to {file_name}')
