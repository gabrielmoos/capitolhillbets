
import pandas as pd

current_senators = "https://en.wikipedia.org/wiki/List_of_current_United_States_senators"
former_senators = "https://en.wikipedia.org/wiki/List_of_former_United_States_senators"

current_reps = "https://en.wikipedia.org/wiki/List_of_current_members_of_the_United_States_House_of_Representatives"
#Too many former reps to consider, can come back to it if we believe the data
#is worth it

def scrape_wiki_senate(url, table_num):
    '''
    '''
    df = pd.read_html(url)[table_num][["Party", "State", "Senator"]]
    dic = df.set_index("Senator").T.to_dict("list")

    return dic

def scrape_wiki_reps(url, table_num):
    '''
    '''
    df = pd.read_html(url)[table_num][["Party.1", "District", "Member"]]
    dic = df.set_index("Member").T.to_dict("list")

    return dic

def get_dics():
    '''
    
    Note: Currently the current_dic doesn't usually have middle inital
    whereas the former dic does. I have to fix this
    Also, dictionary values are a list with party then state
    '''
    current_dic_sen = scrape_wiki_senate(current_senators, 5)
    former_dic_sen = scrape_wiki_senate(former_senators, 2)

    dic_reps = scrape_wiki_reps(current_reps, 7)

    #merge dictionaries 
    master_dic_sen = current_dic_sen | former_dic_sen


    return master_dic_sen, dic_reps