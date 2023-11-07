import pandas as pd
import openpyxl
from openpyxl.utils.cell import get_column_letter
from openpyxl.styles import PatternFill, Font

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
    # Export the DataFrame to an Excel file
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        data.to_excel(writer)
        # Reference to the active worksheet (assuming it's the one just written)
        worksheet = writer.sheets['Sheet1']
        # Iterate through columns and set format
        for column in data.columns:
            col_letter = openpyxl.utils.cell.get_column_letter(data.columns.get_loc(column) + 1)
            # Skip columns with Timestamp objects
            if pd.api.types.is_datetime64_any_dtype(data[column]):
                continue
            # Set cell format to percentage if all values are less than or equal to 1
            if (data[column] <= 1).all():
                for row_num in range(2, len(data) + 2):  # +2 because Excel uses 1-indexing and there's a header row
                    cell = worksheet.cell(row=row_num, column=data.columns.get_loc(column) + 1)
                    cell.number_format = '0.00%'
            # Autosize the column
            worksheet.column_dimensions[col_letter].auto_size = True
        # Format header row (assuming header is in row 1)
        for cell in worksheet["1:1"]:
            cell.fill = openpyxl.styles.PatternFill(start_color="000080", end_color="000080", fill_type="solid")
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        # Save changes to the Excel file
        writer.save()
    print(f'Data exported to {file_name}')