from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from flask_session import Session

from api.Classes.account import User


app = Flask(__name__)
app.secret_key = "H7CtF-*hF*f-r6dD^-0gf8"
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

@app.route('/')
def home():
    error = session.get("error", "")
    return render_template('index.html', error_message=error)

@app.route("/dashboard")
def dashboard():
    user_json = session.get("user")
    print(session)
    if user_json:
        usr = User()
        usr.from_json(user_json)
        return render_template('dashboard.html', username=usr.Username)
    else:
        return redirect("/")


@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form['login-username']
        password = request.form['login-password']

        user = User()
        error = user.Login(username, password)

        if user.LoggedIn:
            session["user"] = user.to_json()
            return redirect("/dashboard")
        else:
            session["error"] = error
            return redirect("/")
    else:
        return redirect("/")

@app.route("/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        username = request.form['signup-username']
        password = request.form['signup-password']
        confirm = request.form['confirm-password']

        user = User()
        if password == confirm:
            error = user.signUp(username, password)
        else:
            error = "Passwords don't match"

        if user.LoggedIn:
            session["user"] = user.to_json()
            return redirect("/dashboard")
        else:
            session["error"] = error
            return redirect("/")
    else:
        return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == '__main__':
    app.run(debug=True)
