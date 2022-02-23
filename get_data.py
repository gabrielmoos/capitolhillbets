import json
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

senate_trades = 'https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json'
house_trades = 'https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json'

def get_data(json, date_format, last_pull=None, df=None):
    # date_format is included as an input b/c senate trade dates and house trade dates are formatted differently
    # last_pull must be formatted as YYYY-MM-DD
    json_df = pd.read_json(json)
    ticker_str = ' '.join(json_df['ticker'].unique())
    
    
    if df is not None:
        ticker = [i for i in json_df['ticker'].unique() if i not in set(df['ticker'].unique())]
        ticker_str = ' '.join(ticker)
        
    if last_pull is None:
        
        if date_format:
            earliest_date = datetime.strptime(json_df['transaction_date'].iloc[-1], '%m/%d/%Y') - timedelta(days=20)
            earliest_date = earliest_date.strftime('%Y-%m-%d')
        else:
            earliest_date = json_df['transaction_date'].iloc[-1]
            earliest_date = (datetime.strptime(earliest_date, '%Y-%m-%d') - timedelta(days=20)).strftime('%Y-%m-%d')
    else:
        earliest_date = last_pull
    today = pd.Timestamp("today").strftime('%Y-%m-%d')
    data = yf.download(ticker_str, start=earliest_date, end=today)
    return data

house_df = get_data(house_trades, False)
house_df.to_csv('house_trades.csv', index=False)

senate_df = get_data(senate_trades, True)
senate_df.to_csv('senate_trades.csv', index=False)



# when we run the get_data function and upload that into get_data as an put
# speed up requests by having overlapping requests, python multiprocessing tools
# Something to supress the -- in the df
# Omit earnings as moments of volatility?
