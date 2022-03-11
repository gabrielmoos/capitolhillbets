import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

def get_summary_stats():
    '''
    This function creates a dashboard for our website of winners and losers.
    
    Inputs:
        Nothing calls other functions
        
    Outputs:
        dfs_out (list): a list of data frames of the best and worst trading
            house reps and senators
    '''
    
    
    
    house_scores = '/Users/zachmariani/Desktop/capitolhillbets/house_to_map.csv'
    senate_scores = '/Users/zachmariani/Desktop/capitolhillbets/senate_to_map.csv'
    
    house_df = pd.read_csv(house_scores, index_col=0)
    senate_df = pd.read_csv(senate_scores, index_col=0)
    
    create_party_plots(house_df, True)
    create_party_plots(senate_df)
    
    winners_losers = get_winners_losers(house_df, senate_df)
    
    dfs_out = []
    
    for outcome_dict in winners_losers:
        
        outcome_table = pd.DataFrame(outcome_dict)
        dfs_out.append(outcome_table)
    
    
    return dfs_out
        
        
def create_party_plots(chamber_df, is_house=False):
    '''
    Creates a set of plots and saves them to the templates folder.
    
    Inputs:
        chamber_df (pd DataFrame): df of the specific chamber
        is_house (boolean): tells us if the chamber is house
    
    Outputs:
        Nothing saves the image of the plot via the file path
    '''
    
    count = 0
    
    file_names = {0:'test_senate_df', 1: 'r_senate_df', \
             2: 'd_senate_df', 3:'test_house_df', 4: 'r_house_df', 5:'d_house_df'}
    
    if is_house:
        
        count = 2
        
        test_house_df = chamber_df[chamber_df['Accuracy'] < 1.0]

        r_house_df = chamber_df[chamber_df['Party'] == 'R']
        r_house_df = r_house_df[r_house_df['Accuracy'] <= 1.0]

        d_house_df = chamber_df[chamber_df['Party'] == 'D']
        d_house_df = d_house_df[d_house_df['Accuracy'] <= 1.0]
        
        to_plot = [test_house_df, r_house_df, d_house_df]
        
        for df in to_plot:
            
            plt.figure()
            
            count += 1
            
            x = df['Count']
            y = df['Accuracy']
            plt.scatter(x, y)

            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x,p(x),"r--")
            
            # Change the path so appropriate to add to the webpage            
            
            plt.savefig('/Users/zachmariani/Desktop/capitolhillbets/' + file_names[count] + '.png')
    
    else:
        
        count = 0
        
        test_senate_df = chamber_df[chamber_df['AccuracyAvg'] < 1.0]

        r_senate_df_1 = chamber_df[chamber_df['Party1'] == 'R']
        r_senate_df_1 = r_senate_df_1[r_senate_df_1['Accuracy1'] <= 1.0]

        r_senate_df_2 = chamber_df[chamber_df['Party2'] == 'R']
        r_senate_df_2 = r_senate_df_2[r_senate_df_2['Accuracy2'] <= 1.0]

        d_senate_df_1 = chamber_df[chamber_df['Party1'] == 'D']
        d_senate_df_1 = d_senate_df_1[d_senate_df_1['Accuracy1'] <= 1.0]

        d_senate_df_2 = chamber_df[chamber_df['Party2'] == 'D']
        d_senate_df_2 = d_senate_df_2[d_senate_df_2['Accuracy2'] <= 1.0]        
        
        to_plot = [test_senate_df, (r_senate_df_1, r_senate_df_2), (d_senate_df_1, d_senate_df_2)]
        
        
        for df in to_plot:
            
            if count == 0:
                
                plt.figure()
                
                x = df['CountAvg']
                y = df['AccuracyAvg']
                plt.scatter(x, y)

                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                plt.plot(x,p(x),"r--")
                
                # Change the path so appropriate to add to the webpage
                
                plt.savefig('/Users/zachmariani/Desktop/capitolhillbets/' + file_names[count] + '.png')
                
                count += 1

            else:
                
                plt.figure()
                
                x = df[0]['Count1'].append(df[1]['Count2'])
                y = df[0]['Accuracy1'].append(df[1]['Accuracy2'])
                plt.scatter(x, y)

                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                plt.plot(x,p(x),"r--")
                
                # Change the path so appropriate to add to the webpage                
                
                plt.savefig('/Users/zachmariani/Desktop/capitolhillbets/' + file_names[count] + '.png')
                
                count += 1
    
    
    
def get_winners_losers(house_df, senate_df):
    '''
    Creates dictionaries of the best/worst traders in each chamber based
    on % change in volume of trades after a purchase/sale, % change in 
    ticker price after a purchase/sale, and the number of trades made.
    
    Inputs:
        house_df (pd DataFrame): A data frame of house members
        senate_df (pd DataFrame): A data frame of senators
    
    Outputs:
        house_winners (dict): A dict of house winners
        senate_winners (dict): A dict of senate winners
        house_losers (dict): A dict of house losers
        senate_losers (dict): A dict of senate losers
        
    '''
    
    house_winners = {'Volume':[], 'Accuracy': [], 'Count':[]}
    senate_winners = {'Volume':[], 'Accuracy': [], 'Count':[]}
    house_losers = {'Volume':[], 'Accuracy': [], 'Count':[]}
    senate_losers = {'Volume':[], 'Accuracy': [], 'Count':[]}
    
    for key in house_winners:
        
        house_winners[key] += house_df.nlargest(5, key)['Member'].tolist()
        house_losers[key] += house_df.nsmallest(5, key)['Member'].tolist()
        senate_winners[key] += senate_df.nlargest(5, key+'Avg').index.tolist()
        senate_losers[key] += senate_df.nsmallest(5, key+'Avg').index.tolist()
    
    return house_winners, senate_winners, house_losers, senate_losers
