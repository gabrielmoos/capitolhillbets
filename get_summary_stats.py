import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import plotly.express as px

import get_data 
import analyze_data 
import prepare_map 
import generate_map

def get_dfs(): 
    '''
    grab the _to_map csvs and return 
    them to use other places in this file 
    '''
    house_scores = 'house_to_map.csv'
    senate_scores = 'senate_to_map.csv'
    
    house_df = pd.read_csv(house_scores, index_col=0)

    senate_df = pd.read_csv(senate_scores, index_col=0)

    senate_df = collapse_senate_df(senate_df)

    return house_df, senate_df


def refresh_histogram(metric): 
    '''
    helper function to refresh histogram to show metric of interest 
    writes out interactive histogram as html 
    '''

    house_df, senate_df = get_dfs() 

    house_fig = create_interactive_histogram(house_df, metric, 'HOUSE')
    senate_fig = create_interactive_histogram(senate_df, metric, 'SENATE')

    house_fig.write_html('templates/house_histogram.html')
    senate_fig.write_html('templates/senate_histogram.html')


def get_summary_stats():
    '''
    This function creates a dashboard for our website of winners and losers.
    
    Inputs:
        Nothing calls other functions
        
    Outputs:
        dfs_out (list): a list of data frames of the best and worst trading
          house reps and senators
          3 dfs in here (in order) volume, accuracy, count
    '''
    
    house_df, senate_df = get_dfs()
    
    winners_losers = get_winners_losers(house_df, senate_df)
    
    dfs_out = []
    
    for outcome_dict in winners_losers:
        
        outcome_table = pd.DataFrame(outcome_dict)
        dfs_out.append(outcome_table)

    return dfs_out


def collapse_senate_df(senate_df):
    '''
    Take in a state wide senate_df and returns it with index to be senator 
    '''
    senate_df = senate_df.reset_index() 
    first = senate_df[['index', 'Senator1', 'Party1', 'Assumed Office1', 'Count1', 'Accuracy1', 'Volume1']]
    first.columns = ['state'] + [x[:-1] for x in first.columns[1:]]

    second = senate_df[['index', 'Senator2', 'Party2', 'Assumed Office2', 'Count2', 'Accuracy2', 'Volume2']]
    second.columns = ['state'] + [x[:-1] for x in second.columns[1:]]

    collapsed_df = first.append(second).set_index('Senator')
    collapsed_df = collapsed_df.dropna(how='all', axis = 1)

    return collapsed_df 


def create_party_plots(chamber_df, chamber):
    '''
    Creates a set of plots and saves them to the templates folder.
    
    Inputs:
        chamber_df (pd DataFrame): df of the specific chamber
        chamber: str either 'HOUSE' or 'SENATE' 
    
    Outputs:
        Nothing saves the image of the plot via the file path
    '''
    
    plt.figure()

    versions = ['R', 'D']
    color_dict = {'R': 'crimson', 'D': 'navy'}

    for version in versions: 

        temp_df = chamber_df[chamber_df['Party'] == version]
        bubble_size = temp_df['Count']
        x = temp_df['Volume']
        y = temp_df['Accuracy']
        
        plt.scatter(x,y,s = bubble_size, \
            color = color_dict[version], alpha = 0.25)
    
        plt.scatter(x.mean(), y.mean(), s = bubble_size.mean(), \
            color = color_dict[version], edgecolors = 'black',label = 'Mean ' + version, alpha =0.75)
        plt.scatter(x.median(), y.median(), s = bubble_size.median(), \
            color = color_dict[version], edgecolors = 'black',label = 'Median ' + version, alpha =0.75)

    plt.xlim([0, 2])
    plt.title('Quality of Trades in the ' + chamber.capitalize())
    plt.xlabel('Volume Score')
    plt.ylabel('Accuracy Score')
    plt.legend(title = 'Count')
    if chamber == 'HOUSE': 
        plt.ylim([-0.33, 0.33])

    plt.savefig('static/' + chamber + '.jpeg', dpi = 500, format='jpeg')
 
    
def get_winners_losers(house_df, senate_df):
    '''
    Creates dictionaries of the best/worst traders in each chamber based
    on ratio in volume of trades after vs. before a purchase/sale, % change in 
    ticker price after a purchase/sale, and the number of trades made.
    
    Inputs:
        house_df (pd DataFrame): A data frame of house members, indexed by congressional district
        senate_df (pd DataFrame): A data frame of senators, indexed by senator (already collapsed) 
    
    Outputs:
        house_winners (dict): A dict of house winners
        senate_winners (dict): A dict of senate winners
        house_losers (dict): A dict of house losers
        senate_losers (dict): A dict of senate loser
    '''

    house_winners = {'Volume':[], 'Accuracy': [], 'Count':[]}
    senate_winners = {'Volume':[], 'Accuracy': [], 'Count':[]}
    house_losers = {'Volume':[], 'Accuracy': [], 'Count':[]}
    senate_losers = {'Volume':[], 'Accuracy': [], 'Count':[]}
    
    for key in house_winners:
        
        house_winners[key] += house_df.nlargest(5, key)['Member'].tolist()
        house_losers[key] += house_df.nsmallest(5, key)['Member'].tolist()
        senate_winners[key] += senate_df.nlargest(5, key).index.tolist()
        senate_losers[key] += senate_df.nsmallest(5, key).index.tolist()
    
    return house_winners, senate_winners, house_losers, senate_losers


def create_interactive_histogram(chamber_df, metric, chamber): 
    '''
    chamber_df (already collapsed senate)
      and makes an html interactive histogram to explore data 
    metric: string either count, volume or accuracy
    chamber: str HOUSE or SENATE 
    '''
    chamber_df = chamber_df.reset_index()
    rs = chamber_df[chamber_df['Party'] == 'R'][metric.capitalize()]
    ds = chamber_df[chamber_df['Party'] == 'D'][metric.capitalize()]

    new_df = pd.DataFrame({'Republicans':rs, 'Democrats': ds})

    new_df = new_df.melt(ignore_index=False).\
        rename({'variable':'Party', 'value':metric}, axis = 1)

    if metric == 'Count': 
        title = 'Trade count in the ' + chamber.capitalize() 
    else: 
        title = 'Histogram of ' + metric + ' score in the ' + chamber.capitalize()

    fig = px.histogram(new_df, x = metric, color = 'Party',\
        color_discrete_map = {'Republicans':'#FF0000', 'Democrats':'#0000ff'},\
        title = title )

    if metric == 'Count': 
        fig.update_yaxes(visible=False)

    return fig