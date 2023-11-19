import pandas as pd
from openbb_terminal.sdk import openbb


def get_dataframes(ticker):
    # Data Fetching
    try:
        cash_flow = openbb.stocks.fa.cash(symbol=ticker)
        income = openbb.stocks.fa.income(ticker)
        balance = openbb.stocks.fa.balance(symbol = ticker)
        growth_ratios = openbb.stocks.fa.growth(ticker)
        earnings = openbb.stocks.fa.earnings(ticker, quarterly = True)
        statements = openbb.stocks.fa.sec(ticker)
        ratios = openbb.stocks.fa.ratios(ticker)
        key_metrics = openbb.stocks.fa.key(ticker)
    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")
        return {}

    # Data frame mapping
    dataframes_mapping = {
        'cash_flow': cash_flow,
        'income': income,
        'balance': balance,
        'growth_ratios': growth_ratios,
        'ratios': ratios,
        'keyMetrics': key_metrics
    }
    return dataframes_mapping