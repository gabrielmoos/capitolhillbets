
import pandas as pd

current_senators = "https://en.wikipedia.org/wiki/List_of_current_United_States_senators"
former_senators = "https://en.wikipedia.org/wiki/List_of_former_United_States_senators"

def scrape_wiki(url, table_num):
    '''
    '''
    df = pd.read_html(url)[table_num][["Party", "State", "Senator"]]
    dic = df.set_index("Senator").T.to_dict("list")

    return dic

def get_dics():
    '''
    
    Note: Currently the current_dic doesn't usually have middle inital
    whereas the former dic does. I have to fix this
    Also, dictionary values are a list with a single element due to how
    the pandas to_dict method works
    '''
    current_dic = scrape_wiki(current_senators, 5)
    former_dic = scrape_wiki(former_senators, 2)

    #merge dictionaries 
    master_dic = current_dic | former_dic


    return master_dic