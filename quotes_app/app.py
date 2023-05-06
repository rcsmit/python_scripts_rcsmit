from flask import Flask, render_template, jsonify
import pandas as pd
import random

app = Flask(__name__)

@app.route('/')
def index():
    # get a random quote from the quotes list
    quote = get_quote()
    return render_template('index.html', quote=quote)

def random_color():
    # generate a random color in hexadecimal format
    return '#' + ''.join(random.choices('0123456789ABCDEF', k=6))

def get_quotes():

    sheet_id  = "1WUqlvJWQ3vaM0NRhXiFkmLgAxhCEkBRzVrkZHHDwuCk"
    sheet_name = "quotes"
    # https://docs.google.com/spreadsheets/d/1WUqlvJWQ3vaM0NRhXiFkmLgAxhCEkBRzVrkZHHDwuCk/edit?usp=sharing
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    quotes = pd.read_csv(url, delimiter=",")
    quotes = quotes.dropna()
    return list(quotes['quote'])

@app.route('/get_quote')
def get_quote():
    quotes = get_quotes()
    quote = random.choice(quotes)
    return jsonify({'quote': quote})
if __name__ == '__main__':
    app.run(debug=True)
