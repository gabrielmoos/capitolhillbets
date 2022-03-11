import json
from matplotlib import ticker
import pandas as pd 
import numpy as np
from collections import Counter
import yfinance as yf
import signal
from datetime import datetime, timedelta

########### STATIC VARIABLES ########################
SECONDS_TO_WAIT = 60 * 10

HOUSE_URL = 'https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json'
SENATE_URL = 'https://senate-stock-watcher-data.s3-us-west-2.amazonaws.com/aggregate/all_transactions.json'

HOUSE_PATHS = ['house_data_adjclose.csv', 'house_data_volume.csv']
SENATE_PATHS = ['senate_data_adjclose.csv', 'senate_data_volume.csv']

#####################################################

def refresh_raw_data(): 
    '''
    This function refreshed all of the 'raw' data 
    from the house and senate stock watcher websites and 
    then stores them locally to avoid having to scrape multiple times 
    '''
    house_raw = pd.read_json(HOUSE_URL)
    senate_raw = pd.read_json(SENATE_URL)
    
    house_raw.to_csv('house_raw.csv', index=False, encoding='utf-8') 
    senate_raw.to_csv('senate_raw.csv', index = False, encoding='utf-8')


def signal_handler(signum, frame):
    '''
    This function helps prevent timing out when pulling 
    data from yfinance 
    '''
    raise Exception("Timed out!")


def get_ticker_data(tickers, start_date, end_date): 
    '''
    Take in an array or list of tickers as strs 
    i.e. ['AAPL', 'MSFT', ...]

    start_date: a string formatted as %Y-%m-%d
    end_date: a string formatted as %Y-%m-%d

    Returns: a pd df where the columns are different tickers' 
    Adj Close, Volume, Open, High, Low 
    and the rows are dates between start_date and end_date 
    '''

    #if any attempt takes more than SECONDS_TO_WAIT 
    #then abort ... sometimes the yfinance API times out 
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(SECONDS_TO_WAIT)   
    try: 
        print('Now attempting to gather data, \n should take about 3-4 minutes per 1,000 tickers')
        data = yf.download(' '.join(tickers), \
                            start = start_date, \
                            end = end_date, \
                            threds = False, \
                            rounding = True)
    except: 
        print('Timed out!')
        print('Please try again, consider your wifi connection or increasing the SECONDS_TO_WAIT variable')
        exit()

    #to.csv works much better with str indexes instead of 
    data.index = pd.to_datetime(data.index).strftime("%Y-%m-%d")
    return data 


def run_chamber_downloads(raw_chamber, chamber_paths): 
    '''
    raw_chamber: raw pd dataframe of the chamber stored locally 
      taken from the house/senate watcher website 
    chamber_paths: a list of file paths 
      [chamber_adjclose.csv, chamber_volume.csv]
    
    Gets the start date that we need, if we have nothing 
    stored we use the earliest date from the raw data 
    if we have something stored, we use the last date stored 

    We run a first run to grab ticker adjclose and vol 
    data from yf, and then a second run to try to 
    catch errors 

    We then try to add these to any legacy data we have stored 
    locally, and then save to the file paths we took in 
    '''

    full_tickers = raw_chamber['ticker'].unique() 

    try: 
        start_dates = []
        old_data = {}
        for chamber_path in chamber_paths: 
            old_data[chamber_path] = pd.read_csv(chamber_path, index_col=0).sort_index()
            start_dates.append(old_data[chamber_path].index[-1])

        #get the earlier of the two possible start dates 
        start_date = min(start_dates)
        
    except Exception as e: 
        print('We were unable to recover old data, error msg:', e)

        #get the earliest day of the data from chamber-watcher and then go 
        #20 days earlier, we will use this for later analysis  
        #due to inconsistencies in the reporting and some outliers in the data, 
        #we start at the 10th index to increase efficiency of code 
        start_date = pd.to_datetime( sorted(raw_chamber['transaction_date'])[10])
        start_date = start_date - timedelta(days = 20)
        start_date = start_date.strftime("%Y-%m-%d")        
    
    end_date = pd.to_datetime("today").strftime("%Y-%m-%d")
    
    print('The start date is:', start_date)
    print('The end date is:', end_date)

    #there are definitely smarter ways to handle errors
    #we opt to just rerun the program with all of the tickers 
    #that we missed once 
    first_run = get_ticker_data(full_tickers, start_date, end_date)

    tickers_to_rerun = first_run['Adj Close'].columns[first_run['Adj Close'].isnull().all()].tolist()
    
    first_run = first_run.dropna(how = 'all', axis = 1)

    second_run = get_ticker_data(tickers_to_rerun, start_date, end_date) 
    
    metric_dict = {0: 'Adj Close', 
                   1: 'Volume'}

    for n, chamber_path in enumerate(chamber_paths): 

        metric = metric_dict[n]

        if second_run.empty: 
            new_data = first_run[metric]
        else: 
            new_data = pd.concat([first_run[metric], second_run[metric]], axis = 1)

        try: 
            refreshed_data = old_data[chamber_path].append(new_data).drop_duplicates()
        except Exception as e: 
            print('Unable to add to legacy data error msg:', e)
            refreshed_data = new_data 
        
        refreshed_data.to_csv(chamber_path)
        print('Finished sans error')
        print('--------------------------------------------------------------------------------------------------------')


def refresh_stock_data(house = True, senate = True):
    '''
    house: bool to refresh house_data 
    senate: bool to refresh senate_data 

    refreshes the raw data stored locally 
    then runs full program 
    '''
    
    refresh_raw_data()

    if house: 
        raw_chamber = pd.read_csv('raw_house.csv')
        run_chamber_downloads(raw_chamber, HOUSE_PATHS)

    if senate:
        raw_chamber = pd.read_csv('raw_senate.csv')
        run_chamber_downloads(raw_chamber, SENATE_PATHS)
