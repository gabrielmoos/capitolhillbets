#from msilib import datasizemask
import pandas as pd 
import numpy as np 

import get_data 

######################## STATIC VARIABLES ##############################

METRIC_DICT = \
    {0 : 'Adj Close', 
    1 : 'Volume'}

HOUSE_PATHS = ['house_data_adjclose.csv', 'house_data_volume.csv']
SENATE_PATHS = ['senate_data_adjclose.csv', 'senate_data_volume.csv']

############################################################################

def start_analyze_data():
    '''
    Helper function to call analyze data from outside
    takes in the raw data and begins to 
    prepare for analysis by adding metrics, we will later map to 
    Polygons for presentation
    '''

    #get raw_data 
    print('Beginning analyze_data')

    try: 
        RAW_DATA = {'HOUSE' : pd.read_csv('house_raw.csv'), 
                    'SENATE' : pd.read_csv('senate_raw.csv')}
        
    except: 
        print('Could not find raw data')
        get_data.refresh_raw_data()
        RAW_DATA = {'HOUSE' : pd.read_csv('house_raw.csv'), 
                    'SENATE' : pd.read_csv('senate_raw.csv')}


    #get house and senate stock data 
    try: 
        HOUSE_DATA = ['house_data_adjclose.csv', 'house_data_volume.csv']
        HOUSE_DATA = [pd.read_csv(file, index_col=0) for file in HOUSE_DATA]

        SENATE_DATA = ['senate_data_adjclose.csv', 'senate_data_volume.csv']
        SENATE_DATA = [pd.read_csv(file, index_col=0) for file in SENATE_DATA]

        chamber_dict = \
        {'HOUSE' : HOUSE_DATA, 
        'SENATE' : SENATE_DATA}

        print('We were able to locate the house and senate stock data!')

    except Exception as e: 
        print('We were unable to locate the house and senate stock data')
        print('Error message:', e)
        print('Please make sure that there is data')
        print('We will now attempt to get data')

        get_data.run_chamber_downloads(RAW_DATA['HOUSE'], HOUSE_PATHS)
        get_data.run_chamber_downloads(RAW_DATA['SENATE'], SENATE_PATHS)
        print('Please rerun analyze data')
        exit() 

    return chamber_dict, RAW_DATA


def get_scores(chamber, metric, chamber_dict, RAW_DATA, n = 5):
    '''
    chamber (str): either HOUSE or SENATE 
    metric: int 0 or 1 
      0 is adj close and trading performance n days prior 
      1 is volume prediction 
    n: int (default 5 for 1 trading week)
      performance of stock n days after trade 

    returns: processed_df 
      index: (transaction_date, ticker)
      row: (amt, asset_description, member, type (long/short), value(performance score))
    '''

    stock_data = chamber_dict[chamber][metric]
    stock_data.index.name = 'transaction_date'
    stock_data.index = pd.to_datetime(stock_data.index)

    if metric == 0: #n beats 
        stock_data = stock_data.pct_change(n)
    
    if metric == 1: #volume spike predictors 
        stock_data = stock_data.fillna(method = 'ffill')
        past_n = stock_data.rolling(n).mean()
        future_n = stock_data.rolling(n).mean().shift(-n)
        stock_data = future_n / past_n
        
    stock_data = stock_data.reset_index()
    stock_data = pd.melt(stock_data, id_vars = 'transaction_date').rename({'variable':'ticker'}, axis = 1)
    stock_data = stock_data.set_index(['transaction_date', 'ticker'])

    raw_data = RAW_DATA[chamber]
    raw_data['transaction_date'] = pd.to_datetime(raw_data['transaction_date'], errors = 'coerce')
    raw_data = raw_data.set_index(['transaction_date', 'ticker'])

    if chamber == 'SENATE': 
        #house data only has stocks, senate has a variety of public and private asset 
        #classes which are extraneous for this project 
        raw_data = raw_data[ (raw_data['asset_type'] == 'Stock') | (raw_data['asset_type'] == 'Stock Option') ]

    raw_data['type'] = raw_data['type'].str.lower()
    raw_data['type'] = raw_data['type'].str.replace(' ', '_', regex=True)
    raw_data['type'] = raw_data['type'].str.replace('(', '', regex=True)
    raw_data['type'] = raw_data['type'].str.replace(')', '', regex=True)
    raw_data['type'] = raw_data['type'].map({
        'purchase' : 1, 
        'sale_full' : -1, 
        'sale_partial' : -1
    })
    raw_data = raw_data[(raw_data['type'] == 1) | (raw_data['type'] == -1)]
    processed_df = raw_data.merge(stock_data, left_index = True, right_index=True)

    return processed_df 


def run_scores(CHAMBER, keyword, file_path, n = 5): 
    '''
    n: int can be used to change look forward window
    helper function to analyze all 4 combinations 
    and save them to avoid having to rerun code 
    '''

    c0 = get_scores(CHAMBER, 0, n)
    c0.replace([np.inf, -np.inf], np.nan, inplace=True)
    c0.fillna(0, inplace = True)

    c0['value'] = c0['value'] * c0['type']
    ccount = c0.groupby(keyword).count()[['value']].rename({'value':'Count'}, axis = 1)
    c0 = c0.groupby(keyword).mean()[['value']].rename({'value':'Accuracy'}, axis = 1)

    c1 = get_scores(CHAMBER, 1, n)
    c1.replace([np.inf, -np.inf], np.nan, inplace=True)
    c1.fillna(0, inplace = True)
    c1 = c1.groupby(keyword).mean()[['value']].rename({'value':'Volume'}, axis = 1)

    chamber_df = pd.concat([ccount, c0, c1], axis = 1)
    chamber_df.to_csv(file_path)
    print('finished!', file_path)


def run_full_analyze_data(): 
    '''
    Runs the full analyze data, easy to call from outside 
    '''
    chamber_dict, RAW_DATA = start_analyze_data()
    run_scores('HOUSE', 'district', 'house_scores.csv', chamber_dict, RAW_DATA, 5)
    run_scores('SENATE', 'senator', 'senate_scores.csv', chamber_dict, RAW_DATA, 5)






