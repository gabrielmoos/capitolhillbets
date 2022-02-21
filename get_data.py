import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

senate_trades = 'https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json'
house_trades = 'https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json'

def get_data(json, date_format):
    # date_format is included as an input b/c senate trade dates and house trade dates are formatted differently
    json_df = pd.read_json(json)
    ticker_str = ' '.join(json_df['ticker'].unique())
    if date_format:
        earliest_date = datetime.strptime(json_df['transaction_date'].iloc[-1], '%m/%d/%Y') - timedelta(days=20)
        earliest_date = earliest_date.strftime('%Y-%m-%d')
    else:
        earliest_date = json_df['transaction_date'].iloc[-1]
        earliest_date = (datetime.strptime(earliest_date, '%Y-%m-%d') - timedelta(days=20)).strftime('%Y-%m-%d')
    today = pd.Timestamp("today").strftime('%Y-%m-%d')
    data = yf.download(ticker_str, start=earliest_date, end=today)
    return data

house_df = get_data(house_trades, False)
house_df.to_csv('house_trades.csv', index=False)

senate_df = get_data(senate_trades, True)
senate_df.to_csv('senate_trades.csv', index=False)

#hello