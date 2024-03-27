from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
import requests
import os
from flask_bcrypt import check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///dss_usersdb'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "iknowwhatyoudidlastsummer"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Define routes after creating the app object


debug = DebugToolbarExtension(app)


# app.app_context().push()
with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def index():
    # Fetch initial quote
    quote = fetch_quote()
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    # Get the submitted user data from the form
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate the data
    if not (username and email and password):
        flash('All fields are required', 'error')
        return redirect('/')

    # Check if the user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already exists. Please log in.', 'error')
        return redirect('/')

    # Create a new user object
    new_user = User(
        username=username,
        email=email,
        password=password
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Redirect to a success page or display a success message
    flash('User successfully registered!', 'success')
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    # Get the submitted user data from the form
    email = request.form.get('login_email')
    password = request.form.get('login_password')

    # Validate the data
    if not (email and password):
        flash('Email and password are required', 'error')
        return redirect('/')

    # Check if the user exists
    user = User.query.filter_by(email=email).first()
    # if not user or user.password != password:
    if not user or not check_password_hash(user.password, password):
        flash('Invalid email or password', 'error')
        return redirect('/')

    # Log in the user
    session['user_id'] = user.id

    # Redirect to a success page or display a success message
    flash('Logged in successfully!', 'success')
    return redirect('/journal')


@app.route('/get_quote')
def get_quote():
    # Fetch and return new quote
    quote = fetch_quote()
    return render_template('journal.html', user=user, quote=quote)


def fetch_quote():
    try:
        response = requests.get('https://stoic.tekloon.net/stoic-quote')
        data = response.json()
        return data['quote']
    except Exception as e:
        return f"Error fetching quote: {e}"


@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    # Get the submitted user data from the form
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate the data
    if not (username and email and password):
        flash('All fields are required', 'error')
        return redirect('/')

    # Create a new user object
    new_user = User(
        username=username,
        email=email,
        password=password
    )

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # Redirect to a success page or display a success message
    flash('User successfully registered!', 'success')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
