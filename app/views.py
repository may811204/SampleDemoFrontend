from flask import render_template
from app import app
import csv



def load_csv():
    d = {}
    line_count = 0
    with open('app/static/data/data.csv') as f:
        reader = csv.DictReader(f)
        for line in reader:
            d[line_count] = line
            line_count += 1
    return d

@app.route('/submit', methods=['POST'])
def retreive_data():
    print("submit here")
    print(request.args)

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    # Renders index.html.
    return render_template('index.html', params=load_csv())
