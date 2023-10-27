import pandas as pd
from openbb_terminal.api import openbb

def get_dataframes(ticker):
    # Data Fetching
    cash_flow = openbb.stocks.fa.cash(symbol=ticker)
    income = openbb.stocks.fa.income(ticker)
    balance = openbb.stocks.fa.balance(symbol = ticker)
    growth_ratios = openbb.stocks.fa.growth(ticker)
    earnings = openbb.stocks.fa.earnings(ticker, quarterly = True)
    statements = openbb.stocks.fa.sec(ticker)
    ratios = openbb.stocks.fa.ratios(ticker)
    key_metrics = openbb.stocks.fa.key(ticker)

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
