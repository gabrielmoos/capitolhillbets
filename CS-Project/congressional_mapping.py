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

states = gpd.read_file('/Users/gmoos19/Downloads/tl_2021_us_state/tl_2021_us_state.shp')
districts = gpd.read_file('/Users/gmoos19/Downloads/tl_2021_us_cd116/tl_2021_us_cd116.shp')

regions = {'Index': ['1','2','3','4'], 'Region': ['Northeast','Midwest', 'South','West']}
r_df = pd.DataFrame(regions)

def get_congress_data():

    r = requests.get("https://www.nrcs.usda.gov/wps/portal/nrcs/detail/?cid=nrcs143_013696")
    soup = BeautifulSoup(r.content)
    soup.find_all('th')
    names = []
    postal_codes = []
    FIPS = []
    names.append(str(soup.find_all('th')[0]).replace('<th scope="col">',"").replace('</th>',"").replace('\r\n\t\t\t\t',""))
    postal_codes.append(str(soup.find_all('th')[1]).replace('<th scope="col">',"").replace('</th>',"").replace('\r\n\t\t\t\t',""))
    FIPS.append(str(soup.find_all('th')[2]).replace('<th scope="col">',"").replace('</th>',"").replace('\r\n\t\t\t\t',""))
    fp_list = soup.find_all('td')
    for i in range(30,195,3):
        names.append(str(fp_list[i]).replace("</td>","").replace('<td>\r\n\t\t\t\t',""))
        postal_codes.append(str(fp_list[i+1]).replace("</td>","").replace('<td>\r\n\t\t\t\t',""))
        FIPS.append(str(fp_list[i+2]).replace("</td>","").replace('<td>\r\n\t\t\t\t',""))
        
    state_fps = {names[0]: names[1:], postal_codes[0]: postal_codes[1:], FIPS[0]: FIPS[1:]}
    state_fps_df = pd.DataFrame(state_fps)
    
    return state_fps_df

