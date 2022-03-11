from flask import Flask, render_template, request
import folium
import json 
import plotly 
import plotly.express as ex 
import pandas as pd

import get_data 
import analyze_data 
import prepare_map 
import generate_map
import get_summary_stats

house_headers = ['District', 'Member', 'Party', 'Assumed office', 'Count', 'Accuracy', 'Volume']
senate_headers = ['State Name',\
    'Senator1', 'Party1', 'Assumed Office1', 'Count1', 'Accuracy1', 'Volume1',\
    'Senator2', 'Party2', 'Assumed Office2', 'Count2', 'Accuracy2', 'Volume2',\
    'Party', 'CountAvg', 'AccuracyAvg', 'VolumeAvg',]

col_headers = {'House' : house_headers, 
                'Senate' : senate_headers}

df_file_names = {0:'house_winners', 1:'senate_winners', 2:'house_losers', 3:'senate_losers'}

cell_hover = {  # for row hover use <tr> instead of <td>
    'selector': 'td:hover',
    'props': [('background-color', '#ffcccb')]
}
index_names = {
    'selector': '.index_name',
    'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
}
headers = {
    'selector': 'th:not(.index_name)',
    'props': 'background-color: #000066; color: white;'
}


app = Flask(__name__, static_url_path='/static')

app.debug = True


@app.route('/', methods=['GET', 'POST'])
def home():

    #collect target metric, what user is interested in of 3 
    target_metric = request.form.get('metric')

    #filter down all the avaiable data by chamber and state 
    chamber_filter = request.form.get('chamber')
    state_filter = request.form.get('state')

    #see if user is interested in refreshing data 
    refresh_data = request.form.get('btn_name')

    if target_metric:
        generate_map.gen_map('SENATE', target_metric)
        generate_map.gen_map('HOUSE', target_metric)
        
        get_summary_stats.refresh_histogram(target_metric)

        return render_template('home.html')
    
    if chamber_filter:
        if state_filter: 
            df = pd.read_csv(chamber_filter.lower() + '_to_map.csv', index_col=0)
            if chamber_filter == 'House':
                df = df[df['STATEFP'] == state_filter]
            if chamber_filter == 'Senate': 
                df = df[df['State Name'] == state_filter]

            df = df[col_headers[chamber_filter]]

            df = df.style.set_table_styles([cell_hover, index_names, headers])
            
            df.to_html('templates/filter.html')
            return render_template('home.html')

    if refresh_data == 'Refresh Data':

        print('Beginning Refresh Data!')
        get_data.refresh_raw_data() 
        get_data.refresh_stock_data()
        analyze_data.run_full_analyze_data()
        prepare_map.run_full_prepare_map()
    
    dfs_out = get_summary_stats.get_summary_stats()

    for i, outcome_df in enumerate(dfs_out):
        #this gives us the ordering we want on the website 
        outcome_df.index = outcome_df.reset_index().index + 1
        outcome_df = outcome_df.style.set_table_styles([cell_hover, index_names, headers])
        outcome_df.to_html('templates/' + df_file_names[i] + '.html')

    return render_template('home.html')

@app.route('/filter/', methods = ['GET', 'POST'])
def filter():
    return render_template('filter.html') 

@app.route('/senate_histogram/', methods=['GET', "POST"])
def senate_histogram(): 
    return render_template('senate_histogram.html')

@app.route('/house_histogram/', methods=['GET', "POST"])
def house_histogram(): 
    return render_template('house_histogram.html')

@app.route('/SENATE_map/', methods = ['GET', 'POST'])
def SENATE_map():
    return render_template('SENATE_map.html')

@app.route('/HOUSE_map/', methods = ['GET', 'POST'])
def HOUSE_map():
    return render_template('HOUSE_map.html')

@app.route('/house_winners/', methods = ['GET', 'POST'])
def house_winners():
    return render_template('house_winners.html')

@app.route('/senate_winners/', methods = ['GET', 'POST'])
def senate_winners():
    return render_template('senate_winners.html')

@app.route('/house_losers/', methods = ['GET', 'POST'])
def house_losers():
    return render_template('house_losers.html')

@app.route('/senate_losers/', methods = ['GET', 'POST'])
def senate_losers():
    return render_template('senate_losers.html')

if __name__ == '__main__':
    app.run(debug=True)