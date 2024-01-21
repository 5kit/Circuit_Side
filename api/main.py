from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from flask_session import Session
import pandas as pd
import json

from api.Classes.account import User


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

df = pd.read_csv('api/Classes/component.csv')

@app.route('/')
def home():
    error = session.get("error", "")
    return render_template('index.html', error_message=error)

@app.route("/dashboard", methods=["GET"])
def dashboard():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        data = json.loads(user_json).get("projects")
        Dc = df[['Code','Name']].to_dict(orient='index')
        return render_template('dashboard.html', username=usr.Username, projects=data, Docs=Dc)
    else:
        return redirect("/")

@app.route('/editor', methods=['POST'])
def editor():
    n = int(request.form.get('project_id'))
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        usr.load_projects()
        return render_template("editor.html", Title=usr.projects[n].Title, Circuit=usr.projects[n].circuit)
    else:
        return redirect("/")
    
@app.route('/documentation', methods=["POST"])
def document():
    id = request.form.get("comp_id")
    print(1, id)
    Dc = list(df[df['Code'] == id].to_dict(orient='index').values())[0]
    print(2, Dc)
    return render_template("document.html", name=Dc["Name"], info=Dc["Description"])

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        # Get user input
        username = request.form['login-username']
        password = request.form['login-password']

        # Make an instance of the class and attempt to login
        user = User()
        error = user.Login(username, password)

        if user.LoggedIn:
            # Save the user details in json format
            session["user"] = user.to_json()
            return redirect("/dashboard")
        else:
            # Show an error
            session["error"] = error
            return redirect("/")
    else:
        return redirect("/")

@app.route("/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        # Get user input
        username = request.form['signup-username']
        password = request.form['signup-password']
        confirm = request.form['confirm-password']

        # Make an instance of the class and evaluate input
        user = User()
        if password == confirm:
            error = user.signUp(username, password)
        else:
            error = "Passwords don't match"

        if user.LoggedIn:
            # Save user details in json format
            session["user"] = user.to_json()
            return redirect("/dashboard")
        else:
            # Show an error
            session["error"] = error
            return redirect("/")
    else:
        return redirect("/")

@app.route("/create_project", methods=["POST"])
def CreateProject():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        usr.create_projects()
        session["user"] = usr.to_json()
        return redirect("/dashboard")
    else:
        return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)