# Custom module to enable basic website functionality -- login check, DB connection and email validation

# Import required Flask modules
from flask import g, redirect, request, session, url_for

# Import wraps module to enable login required decorator
from functools import wraps

# Import re module for regex functionality supporting email validation
import re

# Import sqlite3 module for DB operations
import sqlite3

# Decorator to ensure user is logged in before accessing site features
def login_required(f):
    # Decorate routes to require login.
    # https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Function to connect to database and allow name based access to DB columns
# https://www.digitalocean.com/community/tutorials/how-to-use-an-sqlite-database-in-a-flask-application
def get_db_connection():
    conn = sqlite3.connect('languages.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to validate email address
def validate(email):

    # Use regular expression to check email address
    # https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if(re.fullmatch(regex, email)):
        return True
    else:
        return False
