from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Entry
import requests
import os
from flask_bcrypt import check_password_hash
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///dss_usersdb'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "iknowwhatyoudidlastsummer"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Define routes after creating the app object


debug = DebugToolbarExtension(app)
bcrypt = Bcrypt(app)

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
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Validate the data
    if not (email and password):
        flash('Email and password are required', 'error')
        return redirect('/')

    # Check if the user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Invalid email or password', 'error')
        return redirect('/')

    is_valid = bcrypt.check_password_hash(hashed_password, password)
    if not is_valid:
        flash('Invalid email or password', 'error')
        return redirect('/')

    # Log in the user
    session['user_id'] = user.id

    # Redirect to the journal page
    return redirect('/journal')


@app.route('/journal')
def journal():
    # Assuming you have the user stored in the session
    user = User.query.get(session.get('user_id'))
    # Fetch and return new quote
    quote = fetch_quote()

    if user:
        # Render the journal.html template with user and quote data
        entries = Entry.query.filter_by(user_id=user.id).order_by(
            Entry.timestamp.desc()).all()
        return render_template('journal.html', user=user, quote=quote, entries=entries)
    else:
        # Handle case where user is not logged in
        flash('You need to log in to access the journal', 'error')
        return redirect('/')


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
    entry_text = request.form.get('entry_text')

    # Validate the data
    if not entry_text:
        flash('Entry text is required', 'error')
        return redirect('/journal')

    # Assuming you have the user stored in the session
    user = User.query.get(session.get('user_id'))

    # Save the entry to the database or do whatever processing you need
    new_entry = Entry(text=entry_text, user=user)
    db.session.add(new_entry)
    db.session.commit()
    flash('Entry submitted successfully!', 'success')
    return redirect('/journal')

    # Get the submitted user data from the form
    # username = request.form.get('username')
    # email = request.form.get('email')
    # password = request.form.get('password')
    # image_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKkAAACUCAMAAADf7/luAAAAMFBMVEW6urr///+3t7fe3t7p6en09PT8/PzT09Pj4+PY2Njv7+/FxcXBwcH5+fnOzs6+vr6sgxMeAAADmklEQVR4nO2b2XLDIAwAjWxu2/z/3xbspHVucwky1T7kIUnbHZlDIHUYCIIgCIIgCIIgiLa4w2vPBEPn3NC9KxxpLfMS7+asHKfJGDNNo7SuR1sXLLVZ2JHF6GDb1TAAmOV0q3mRneTcU2ABtBGMCcHEwVKEN5gwuh9VJ5+F8xBY2ccAADuJt6I+rpPtIKywvg/oJaxre9WRsY8hDV8Y22qCUycCuqNc07CeF/WqDT1hihBlbGoWVBijRP1YbaQKK/s8m/4I32y0Atgzy9Mti21iGjdId6YGniATRNs8f55kytE9QSeJMqaxg+rSQuqDip1XpY3SgEQ2TZn4O8jTfz6/4t8jZkzR5PkUQJ1TkanJLQZ19sdvpH8siJ5gIzKTewRDPFT5nTTHVCKaxiamtyCmqRBzKHlEIU6pnKmPu/Z/janLNMVLUnJN0US/6Ol/z9zPSlBQU5TtpJ8O4qnP7/s5oF6mfksulZefol6kJV5L7CCmUh6XkfUhH6O/5WzqQKYGVUjkop8ziaYG+w4lbFPxYRUN7qXCXV/KAOD4on5HTYlpi/vTpCQVMYk+MMdfTHLUO6lfQp4SMwAEcm7yJ5pUj2pVPFNR9aiW5chhZOKUbPhW42r0+QHQWNTvVeeS6qXB3nSvup5ZrHgHPROhD+WjaBd9KMMlrK/mlegkoEPoNHQwyNdJoJGDz0j76EMKuJc9aP04Xtgb5m560HprlfsldEZaqdUUUFraocdeyV+ucl1LEv+eztukg5WzdpVaj6PaGUet5Wqt2z9ujNstw9JkDF/E/Y4qxMKNUXq1u227TWBr41b8avi49V8/EFxtzd2NNIdZKv7E69U7XMkZ/Rzl/F9cVcIpWq3+JxELZz45GnnaZZ/go8NzBavE86f90XN7UUh5NcwJj/0Wrubqrv7J6VzPzVUPlS98t0NT+h3/FVH9aAXyzYkpUpXXrKHAx/+GiLKtVpiCOa9Y/shUZ2LBnFqEeI2poQqD2YZXqee//ypTYXtNLuu8p3zRJ7RJlJxOO6J8A0Vml8Q7yl4Cgi04Qo+EX1t2Cyi9Ph0pWPIN9dwaAd0RJWu+leb9lXLzP7OV5zPF7lehbkgLdk7PlUUZK1SkrLiWXim0pma1HJ2jUP6XUHOOpUyNGuxSbzHdEUuRfSq9jSdCtcw6VX9C+SlVQjSiiJtOmfLvF5kijNN/F1MyJVMyJVMyJVMyJVMyJVMyJVMyJdOapj8cjTBB4wDNrAAAAABJRU5ErkJggg=="

    # # Validate the data
    # if not (username and email and password):
    #     flash('All fields are required', 'error')
    #     return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
