from flask import Flask, render_template
import folium

app = Flask(__name__)

app.debug = True

@app.route('/')
def home():
    return render_template('first_page.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/test/')
def test():
    return render_template('test.html')

@app.route('/map/')
def map():
    return render_template('congressional_mapping.html')

if __name__ == '__main__':
    app.run(debug=True)