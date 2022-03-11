get_data.py - This file gets the data from Senate Stock Watcher and House Stock Watcher and then pulls
Ticker data from yFinance. Finally it formats the data. It also has a function to get new data.

analyze_data.py - Takes in the raw data from get_data.py. Analyzes the data and then exports the data
Into .csv files

prepare_map.py - A file that scrapes the current house and senate reps from Wikipedia. Then adds data from those sources into a data frame with the shape file coordinates. This is then passed in as a GeoPandas data frame and return as a .csv to be mapped.

generate_map.py - Takes in the .csv files created by prepare_map.py. It then generates a Folium map from the GeoPandas dataframe for both the House and Senate.

get_summary_stats.py - Takes in the .csv files from prepare_map.py and does some analysis to create scatter plots, histograms and tables.

render_webpage.py - Creates a development webpage using Flask.

static - A directory that stores images as .png and .jpeg files

templates - A directory that stores .html files. Iframes are used in our code, so templates contains lots of .html files that are not accessible from the homepage

README.txt - This file.