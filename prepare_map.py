from operator import index
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import math
import geopandas as gpd
import random
from bs4 import BeautifulSoup
import html5lib
import requests
import regex as re
from matplotlib import colors
import unidecode
from mpl_toolkits.axes_grid1 import make_axes_locatable
from fuzzywuzzy import fuzz 
from fuzzywuzzy import process 
import seaborn as sns 

import get_data 
import analyze_data 

################################################### STATIC VARIABLES ##################################################################
US_STATE_TO_ABBR = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}


CURRENT_SENATORS = "https://en.wikipedia.org/wiki/List_of_current_United_States_senators"
CURRENT_REPS = "https://en.wikipedia.org/wiki/List_of_current_members_of_the_United_States_House_of_Representatives"


########################################################################################################################################################

def colormapping(x, y): 
    '''
    A function to help the senate colors be mapped 
    if both representatives are D then map the senate B
    if both are R then map R 
    if one of each then map P 
    '''
    
    if not isinstance(y, str) or x == y:
        return x

    if x!= y: 
        return 'P'


def snscolor_map(party, uniqueq, Q): 
    '''
    Take in a party either 'R', 'D', 'V', 'B' 'P' 
    uniqueq - the quantile of the data 
    Q - the number of quantile buckets 

    returns a string hex color to map 
    '''
    snsncolor_dict = {'R':'Reds', "D": 'Blues', 'B':'Blues', 'V': 'Greys', 'I':'Greys', 'P': 'Purples'}
    return sns.color_palette(snsncolor_dict[party], Q+1).as_hex()[-uniqueq]


def add_color_hex_to_df(df, Q, score_headers):
    '''
    Take in a df to add color hexs to 
    take in Q, how many bins you'd like (shades of each color)
    score_headers a list, if house ['Accuracy', 'Volume', 'Count']
      if senate ['AccuracyAvg', 'CountAvg', 'VolumeAvg']
    Returns the df with the color hexes added
    '''
    df['accuracy_q'] = pd.qcut(df[score_headers[0]], Q, labels=False)
    df['volume_q'] = pd.qcut(df[score_headers[1]], Q, labels=False)
    df['count_q']= pd.qcut(df[score_headers[2]], Q, labels=False)

    df['accuracy_color'] = df.apply(lambda x: snscolor_map(x.Party, x.accuracy_q, Q), axis=1)
    df['volume_color'] = df.apply(lambda x: snscolor_map(x.Party, x.volume_q, Q), axis=1)
    df['count_color'] = df.apply(lambda x: snscolor_map(x.Party, x.count_q, Q), axis=1)

    return df 


def convert_to_SSNN(index): 
    '''
    Takes in an index like ['Alabama 1', ... 'Wyoming at-large']
    returns index like ['AL01', ..., 'WY00']
    '''
    out = []
    for ind in index: 
        ind = ind.replace('at-large', '00')
        
        ind = ind.split(' ')
        num = ind[-1]
    
        if len(num) == 1: 
            num = str(0) + str(num)
        
        long_state = ' '.join(ind[:-1])
        abbr = US_STATE_TO_ABBR[long_state]
        out.append(abbr + str(num))

    return out


def senate_name_match(index1, index2): 
    '''
    Takes in two indexes with senator names slightly different 
      index1 = ['A. Mitchell Mcconnell, Jr.'...]
      index2 = ['Mitch Mcconnell'...]
    and returns a dictionary maping indexs1 : indexs2 
    '''
    out_dict={}
    for ind1 in index1:
        if ind1 in index2:
            out_dict[ind1] = ind1
        else: 
            ind2=process.extractOne(ind1,index2,scorer=fuzz.token_set_ratio)
            out_dict[ind1] = ind2[0]
    return out_dict 


def clean_wiki(wiki, n):  
    '''
    Gets information from wiki page (url) 
    and finds table of interest (nth table)
    to get expanded data like state for senators 
    and years in office for display to users
    '''
    wiki = pd.read_html(wiki)[n]
    if n == 7:
        wiki = wiki[['District', 'Member', 'Party.1', 'Assumed office']]
    elif n == 5:
        wiki = wiki[['State', 'Senator', 'Party.1', 'Assumed office']]

    wiki.rename({'Party.1':'Party'}, axis = 1, inplace=True)
    wiki['Party'] = wiki['Party'].str[0]

    wiki['Assumed office'] = pd.to_datetime(wiki['Assumed office'], errors = 'coerce').dt.strftime('%Y').astype(str)
    wiki['Assumed office'] = [str(x).replace(',', "") for x in wiki['Assumed office']]

    return wiki 


def get_senate_geos(senate_score_df): 
    '''
    Takes in a senate_score_df and merges it with the 
    geopandas data to return a df ready for mapping  

    senate_score_df has index Senator name 
    one column titled value   
    '''

    #first get wiki data 
    senate = clean_wiki(CURRENT_SENATORS, 5)

    #filter mapping data down to only the 50 states 
    states50 = senate['State'].unique()
    states = gpd.read_file('shapes/tl_2021_us_state/tl_2021_us_state.shp')
    states = states[states['NAME'].isin(states50)]
    states = states[['REGION', 'NAME', 'STUSPS', 'geometry']]
    states = states.set_index("NAME")

    clean_senate_wiki = {}

    index1 = senate_score_df.index
    index2 = senate['Senator'].values

    senator_mapping = senate_name_match(index1, index2)
    new_index = [senator_mapping[x] for x in index1]
    senate_score_df.index = new_index 

    senate = senate_score_df.merge(senate, left_index = True, right_on = 'Senator')

    for state in senate['State'].unique(): 

        state_specific = senate[senate['State'] == state]
       
        s0 = state_specific['Senator'].iloc[0]
        p0 = state_specific['Party'].iloc[0]
        a0 = state_specific['Assumed office'].iloc[0]
        count0 = state_specific['Count'].iloc[0]
        acc0 = state_specific['Accuracy'].iloc[0]
        vol0 = state_specific['Volume'].iloc[0]

        #some states have 2 senators which we have data for, 
        #if we can, we collect their data 
        try: 
            s1 = state_specific['Senator'].iloc[1]
            p1 = state_specific['Party'].iloc[1]
            a1 = state_specific['Assumed office'].iloc[1]
            
            count1 = state_specific['Count'].iloc[1]
            acc1 = state_specific['Accuracy'].iloc[1]
            vol1 = state_specific['Volume'].iloc[1]

            clean_senate_wiki[state] = [s0, p0, a0, count0, acc0, vol0, s1, p1, a1, count1, acc1, vol1]
        except Exception as e: 
            clean_senate_wiki[state] = [s0, p0, a0, count0, acc0, vol0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
            
    
    #build full df 
    senate = pd.DataFrame(clean_senate_wiki).transpose().rename({0:'Senator1', 1:'Party1',2: 'Assumed Office1',\
         3:'Count1', 4:'Accuracy1', 5:'Volume1', 6:'Senator2', 7:'Party2', 8:'Assumed Office2', 9:'Count2',\
             10: 'Accuracy2', 11:'Volume2'}, axis = 1)

    #add colors! 
    senate['Party'] = ''
    
    senate['Party'] = senate.apply(lambda x: colormapping(x.Party1, x.Party2), axis=1)
    senate = senate.merge(states, right_index=True, left_index=True)
    
    for metric in ['Count', 'Accuracy', 'Volume']:
        senate[metric+'Avg'] = senate[[col for col in senate.columns if metric in col]].mean(axis = 1)

    senate = add_color_hex_to_df(senate, Q=5, score_headers=['AccuracyAvg', 'CountAvg', 'VolumeAvg'])
    senate['State Name'] = senate.index
    
    senate.to_csv('senate_to_map.csv')


def get_house_geos(house_score_df): 
    '''
    Takes in a house_score_df and merges it with the 
    geopandas data to return a df ready for mapping  

    house_score_df has index 
    one column titled value   
    '''

    house_wiki = clean_wiki(CURRENT_REPS, 7)

    #we need some data from the senate in order to map USPSC to state names etc
    senate_helper = gpd.read_file('shapes/tl_2021_us_state/tl_2021_us_state.shp')
    statefp_to_statename_dict = senate_helper.set_index("STATEFP").to_dict()['NAME']
    
    senate = clean_wiki(CURRENT_SENATORS, 5)
    #filter mapping data down to only the 50 states 
    states50 = senate['State'].unique()
    
    districts = gpd.read_file('shapes/tl_2021_us_cd116/tl_2021_us_cd116.shp')
    
    districts['STATEFP'] = districts['STATEFP'].astype(str) 
    districts['STATEFP'] = districts['STATEFP'].map(statefp_to_statename_dict)
    districts = districts[districts['STATEFP'].isin(states50)] 

    districtnums = districts['NAMELSAD'].str.extract('(\d+)').astype(str)
    districtnums = districtnums.replace('nan', 'at-large')
    districtsindex = districts['STATEFP'] + ' '+ districtnums[0]
    districts.index = districtsindex
    districts.sort_index(inplace=True)

    decoded_index = [unidecode.unidecode(x) for x in house_wiki['District'].astype(str)]
    house_wiki.index = decoded_index 

    merged_house = pd.concat([house_wiki, districts], join = 'inner', axis = 1)
    merged_house.index = convert_to_SSNN(merged_house.index)

    house = merged_house.merge(house_score_df, left_index=True, right_index = True)
    house = add_color_hex_to_df(house, Q=10, score_headers=['Accuracy', 'Volume', 'Count'])

    house.to_csv('house_to_map.csv')


def run_full_prepare_map():
    '''
    Easy to call function to run full prepare map 
    take in _scores and get them _to_map 
    '''
    house_score_df = pd.read_csv('house_scores.csv', index_col = 0)
    senate_score_df = pd.read_csv('senate_scores.csv', index_col = 0)

    get_house_geos(house_score_df)
    get_senate_geos(senate_score_df)
