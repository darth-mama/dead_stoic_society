from flask import Flask, render_template, request
from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db
import requests
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///dss_usersdb'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "iknowwhatyoudidlastsummer"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Define routes after creating the app object


debug = DebugToolbarExtension(app)


app.app_context().push()
with app.app_context():
    connect_db(app)
    db.create_all()


app = Flask(__name__)
db.init_app(app)


@app.route('/')
def index():
    # Fetch initial quote
    quote = fetch_quote()
    return render_template('index.html', quote=quote)


@app.route('/get_quote')
def get_quote():
    # Fetch and return new quote
    quote = fetch_quote()
    return render_template('index.html', quote=quote)


def fetch_quote():
    try:
        response = requests.get('https://stoic.tekloon.net/stoic-quote')
        data = response.json()
        return data['quote']
    except Exception as e:
        return f"Error fetching quote: {e}"


if __name__ == '__main__':
    app.run(debug=True)
