Hello and welcome to Capitol Hill Bet's CS122 Final Project! 
In this file you can find information about the other files in the folder as well as information on how to run our project ! 

In the order they are used in the project: 

1. get_data.py - This file gets the data from Senate Stock Watcher and House Stock Watcher and then pulls
Ticker data from yFinance. Finally it formats the data. It also has a function to get new data.

2. analyze_data.py - Takes in the raw data from get_data.py. Analyzes the data and then exports the data
Into .csv files

3. prepare_map.py - A file that scrapes the current house and senate reps from Wikipedia. Then adds data from those sources into a data frame with the shape file coordinates. This is then passed in as a GeoPandas data frame and return as a .csv to be mapped.

4. generate_map.py - Takes in the .csv files created by prepare_map.py. It then generates a Folium map from the GeoPandas dataframe for both the House and Senate.

5. get_summary_stats.py - Takes in the .csv files from prepare_map.py and does some analysis to create scatter plots, histograms and tables.

6. render_webpage.py - Creates a development webpage using Flask.

Folders: 

static - A directory that stores images as .png and .jpeg files

templates - A directory that stores .html files. Iframes are used in our code, so templates contains lots of .html files that are not accessible from the homepage

README.txt - This file.

To run our website, navigate to the /captiolhillbets folder and then run 
"export FLASK_APP=render_webpage.py”
"export FLASK_ENV=development”
“flask run”
