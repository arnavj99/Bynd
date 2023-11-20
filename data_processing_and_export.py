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

def fetch_selected_metrics(ticker, selected_metrics, dataframes, metrics_mapping, years):
    data = pd.DataFrame(index=[ticker], columns=[f"{metric}_{year}" for year in range(1, years+1) for metric in selected_metrics])  # Initialize DataFrame with ticker as index and metrics as columns
    for metric in selected_metrics:
        if metric in metrics_mapping:
            df_name = metrics_mapping[metric]
            df = dataframes[df_name]
            if metric in df.index:
                for year in range(1, years+1):
                    try:
                        value = df.loc[metric].values[-year]  # Get the value for the specified year
                    except IndexError:
                        value = pd.NA  # Fill with NA if the data for the year is not available
                    # Check if the value is a number and greater than 1000
                    if isinstance(value, (int, float)) and (value > 100000 or value < -100000):
                        value /= 1e6  # Convert to millions
                    elif isinstance(value, str):  # Check if the value is a string
                        try:
                            value = float(value)  # Try converting the string to a float
                            if value > 100000:
                                value /= 1e6  # Convert to millions
                        except ValueError:
                            pass  # Ignore if the string cannot be converted to a float

                    data.loc[ticker, f"{metric}_{year}"] = value  # Store the value in the DataFrame
            else:
                for year in range(1, years+1):
                    data.loc[ticker, f"{metric}_{year}"] = pd.NA  # Fill with NA if the metric is not in the DataFrame
        else:
            for year in range(1, years+1):
                data.loc[ticker, f"{metric}_{year}"] = pd.NA  # Fill with NA if the metric is not in the metrics_mapping
    return data.reset_index().rename(columns={'index': 'ticker'})

def set_cell_format(worksheet, data, column):
    col_letter = openpyxl.utils.cell.get_column_letter(data.columns.get_loc(column) + 1)
    if pd.api.types.is_numeric_dtype(data[column]) and (data[column] <= 1).all():
        for row_num in range(2, len(data) + 2):
            cell = worksheet.cell(row=row_num, column=data.columns.get_loc(column) + 1)
            cell.number_format = '0.00%'
    return worksheet

def autosize_column(worksheet, data, column):
    col_letter = openpyxl.utils.cell.get_column_letter(data.columns.get_loc(column) + 1)
    max_length = max(len(item) for item in data[column].astype(str))
    worksheet.column_dimensions[col_letter].width = max_length + 2
    return worksheet

def format_header_row(worksheet):
    for cell in worksheet["1:1"]:
        cell.fill = openpyxl.styles.PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
        cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
        cell.value = cell.value.title()
    return worksheet

def generate_excel(data, file_name='comparative_analysis.xlsx'):
    with pd.ExcelWriter(file_name, engine='openpyxl') as writer:
        data.to_excel(writer)
        worksheet = writer.sheets['Sheet1']
        for column in data.columns:
            if not pd.api.types.is_datetime64_any_dtype(data[column]):
                worksheet = set_cell_format(worksheet, data, column)
                worksheet = autosize_column(worksheet, data, column)
        worksheet = format_header_row(worksheet)
        writer.save()
    print(f'Data exported to {file_name}')
