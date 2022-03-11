import geopandas as gpd 
import pandas as pd 
import numpy as np
import folium
from shapely.wkt import loads

import get_data 
import analyze_data 
import prepare_map 


def create_map(df, col_headers, target_metric):
    '''
    Take in a chamber_to_map df  
    col_headers list of headers of interest to display
    target_metric one of [count, accuracy, volume]
    ''' 
    
    gdf = gpd.GeoDataFrame(df)
    gdf.geometry = gdf['geometry'].apply(loads)

    mapping = gdf.explore(
        m = folium.Map(location=[48, -102], zoom_start=3, control_scale=False),
        style_kwds={'color':"black", 'fillOpacity' : 1}, # use black outline
        width = '100%',
        color = target_metric+'_color',
        tooltip = col_headers,
        popup = col_headers,
        height = "100%")

    return mapping

def gen_map(chamber, target_metric): 
    '''
    Chamber: choose from "HOUSE" or "SENATE"
    target_metric: choose from 'count', 'accuracy', or 'volume'
    
    saves html of gpd.explore() to CHAMBER_map.html for use on website
    '''

    print('Beginning generate_map.py')

    try: 
        house_to_map = pd.read_csv('house_to_map.csv', index_col=0)
        senate_to_map = pd.read_csv('senate_to_map.csv', index_col=0)
        print('Successfully gathered chamber_to_map.csv s')
    except: 
        print('Unable to find chamber_to_map.csv')
        print('Please resolve by running prepare_map.py and then run again')
        exit()


    house_headers = ['District', 'Member', 'Party', 'Assumed office', 'Count', 'Accuracy', 'Volume']
    senate_headers = ['State Name',\
     'Senator1', 'Party1', 'Assumed Office1', 'Count1', 'Accuracy1', 'Volume1',\
     'Senator2', 'Party2', 'Assumed Office2', 'Count2', 'Accuracy2', 'Volume2',\
     'Party', 'CountAvg', 'AccuracyAvg', 'VolumeAvg',]

    col_headers = {'HOUSE' : house_headers, 
                   'SENATE' : senate_headers}
    
    chamber_df = {'HOUSE' : house_to_map, 
                  'SENATE' : senate_to_map}

    mapping = create_map(chamber_df[chamber], col_headers[chamber], target_metric)
    print('saving: ', 'templates/' + chamber + '_map.html')
    mapping.save('templates/' + chamber + '_map.html')


