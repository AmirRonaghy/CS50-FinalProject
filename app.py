
# Import flask and all required libraries to enable web application
from flask import Flask, jsonify, flash, redirect, url_for, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Import requests to handle URLs
import requests

# Import SQLite3 for DB operations
import sqlite3

# Import time to generate timestamp
import time

# Import custom chatbot module to enable function for generating chatbot dialog
import chatbot
from chatbot import chatbot_response

# Import custom translate module to enable dialog translation function
import translate
from translate import get_translation

# Import custom synthesize module to enable text-to-speect functionality
import synthesize
from synthesize import synthesize_speech

#Import helpers module to enable login, DB connection and email validation
import helpers
from helpers import login_required, get_db_connection, validate

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# JSON configuration recommended in MS Translator tutorial
app.config['JSON_AS_ASCII'] = False

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create database tables for students and sessions if they don't already exist
conn = get_db_connection()
conn.execute('CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, username TEXT NOT NULL, password_hash TEXT NOT NULL, email TEXT NOT NULL)')
conn.execute('CREATE TABLE IF NOT EXISTS sessions (session_id INTEGER PRIMARY KEY, language TEXT NOT NULL, time DATETIME DEFAULT CURRENT_TIMESTAMP, student_id INT NOT NULL, FOREIGN KEY (student_id) REFERENCES students (id))')
conn.close()

# Route users to homepage if not logged in
@app.route("/")
def index():
    return render_template("index.html")

# Route users to select language page upon login
# Greet users and ask them to select a language to practice
@app.route("/select", methods=["GET", "POST"])
@login_required
def select():
    """Retrieve languages from Microsoft Translator translation dictionary and display them in
    drop-down list for user to select"""

    # Load JSON file containing languages supported by Microsoft Translator
    url = "https://api.cognitive.microsofttranslator.com/languages?api-version=3.0&scope=translation"
    response = requests.get(url)
    data = response.json()

    # Iterate through nested dictionaries for each language in translation dictionary
    # Store full name of each language in a list
    languages = []
    for key, value in data["translation"].items():
        languages.append(value["name"])

    # Sort languages list alphabetically
    languages.sort()

    # Select language via POST
    if request.method == "POST":
        # Ensure user has selected a language
        selected_lang = request.form.get("language")
        if not selected_lang:
            flash("Please select a language")
            return render_template("select.html")
        else:
            # Store selected language and user ID into DB
            student_id = session["user_id"]
            conn = get_db_connection()
            conn.execute("INSERT INTO sessions (language, student_id) VALUES (?,?)", (selected_lang, student_id))
            conn.commit()
            conn.close()

            # Iterate through nested dictionaries in translation dictionary and find code for selected language
            for key, value in data["translation"].items():
                # Store code for selected language in session object for retrieval in multiple requests
                if selected_lang == value["name"]:
                    session["langCode"] = key

            # Store full name of selected language in session variable for retrieval in multiple requests
            session["language"] = selected_lang

            # Redirect to conversation page and pass language code and selected language to conversation as arguments
            return redirect(url_for(".conversation"))

    # Display select page via GET
    else:
        return render_template("select.html", languages=languages)

# Conversational practice page in selected language
@app.route("/conversation", methods=["GET", "POST"])
@login_required
def conversation():
    """ Allow student to converse with chatbot character and use translate_text function to
    translate dialog into selected language
    """
    # Retrieve selected language from URL and language code from session object
    langCode = session["langCode"]
    #language = request.args.get("language")

    # Test variables
    language = "fa-IR";
    characterVoice = "Microsoft Server Speech Text to Speech Voice (fa-IR, DilaraNeural)"
    studentVoice = "Microsoft Server Speech Text to Speech Voice (fa-IR, FaridNeural)"

    # Translate conversational greeting into selected language using translation function
    greeting = "Hello! How are you?"
    greetingTranslated = get_translation(greeting, langCode)

    # Convert translated greeting to speech
    synthesize_speech(greetingTranslated, language, characterVoice)
    audioFile = session["audio-file"]

    # Display student dialog, chatbot response and translations via post request
    if request.method == "POST":

        # Grab student dialog from conversation page via Ajax request and translate into selected language
        student = request.form["student"]
        studentTranslated = get_translation(student, langCode)

        # Convert student dialog to speech
        synthesize_speech(studentTranslated, language, studentVoice)
        studentAudio = session["audio-file"]

        # Generate character response to student using chatbot response function and translate into selected language
        character = chatbot_response(student)
        characterTranslated = get_translation(character, langCode)

        # Convert character dialog to speech
        synthesize_speech(characterTranslated, language, characterVoice)
        characterAudio = session["audio-file"]

        # Return character response and all dialog translations
        return jsonify({"character": character, "characterTranslated": characterTranslated, "studentTranslated": studentTranslated, "studentAudio": studentAudio, "characterAudio": characterAudio})

    # Display conversation page via get request
    else:
        # Display conversation page and pass selected language to it as parameter
        return render_template("conversation.html", language=language, greeting=greeting, greetingTranslated=greetingTranslated, audioFile=audioFile)

# History page -- to do

# Show date, time and language of each session
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return render_template("login.html")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        # Query database for username
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM students WHERE username = ?", [request.form.get("username")])
        # Store query in variable to allow retrieval of data
        user = row.fetchone()
        # Close DB connection
        conn.close()

        # Display error if username does not exist
        if user is None:
            flash("Invalid username")
            return render_template("login.html")

        # Store user data in variables for reference in password validation below
        user_id = user[0]
        #username = user[1]
        password = user[2]

        # Ensure password is correct
        if not check_password_hash(password, request.form.get("password")):
            flash("Incorrect password")
            return render_template("login.html")

        # Store user ID in session object to remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to select language page
        return redirect("/select")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Clear user ID when logging out
    session.clear()
    # Redirect user to login form
    return redirect("/")


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Submit user info via post
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # If email address is not entered or is invalid, display error message
        if not email or not validate(email):
            flash("Must provide valid email address")
            return redirect("/register")

        # If username is not entered, reload page and display error message
        if not username:
            flash("Must provide username")
            return redirect("/register")

        # Ensure username is unique
        else:
            conn = get_db_connection()
            rows = conn.execute("SELECT * FROM students WHERE username = ?", [username])
            if rows.fetchone():
                flash("Username already exists")
                return redirect("/register")
            conn.close()

        # Ensure password is entered
        if not password:
            flash("Must provide password")
            return redirect("/register")

        #Ensure passwword has at least 8 characters with at least 1 number and 1 letter
        elif len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            flash("Invalid password")
            return redirect("/register")

        # Ensure password is confirmed
        elif password != request.form.get("confirmation"):
            flash("Passwords do not match")
            return redirect("/register")

        # Insert username and hash of password into user table
        else:
            conn = get_db_connection()
            conn.execute("INSERT INTO students (username, password_hash, email) VALUES(?,?,?)", (username, generate_password_hash(password), email))
            conn.commit()
            # Set session id to log user in automatically
            row = conn.execute("SELECT id FROM students WHERE username = ?", [username])
            new_user = row.fetchone()
            conn.close()
            session["user_id"] = new_user[0]
            # Redirect user to select language page and flash message to confirm registration
            flash("Registered!")
            return redirect("/select")

    # Display registration page via get method
    else:
        return render_template("register.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc', debug=True)
