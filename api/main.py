from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta

from api.Classes.account import User

app = Flask(__name__)
app.secret_key = "H7CtF-*hF*f-r6dD^-0gf8"
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/')
def home():
    error = session["error"]
    return render_template('index.html', error_message = error)

@app.route("/user")
def user():
    if "user" in session:
        user = session["user"].Username
        return render_template('dashboard.html', username=user)
    else:
        return redirect("/")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        usr = request.form['login-username']
        pss = request.form['login-password']
        
        USR = User()
        session["error"] = USR.Login(usr,pss)
        if USR.LoggedIn:
            session.permanent = True
            session["user"] = USR
            return redirect(url_for("user"))
        return redirect("/")
    else:
        return redirect("/")
    
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        usr = request.form['signup-username']
        pss = request.form['signup-password']
        cfm = request.form['confirm-password']
        
        if pss == cfm:
            USR = User()
            session["error"] = USR.signUp(usr,pss)
            if USR.LoggedIn:
                session.permanent = True
                session["user"] = USR
                return redirect(url_for("user"))
            return redirect("/")
        else:
            session["error"] = "Passwords dont match!"
            return redirect("/")
    else:
        return redirect("/")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    if request.method == "POST":
        session["user"].Logout()
        session.pop("user", None)
        return redirect("/")
    else:
        return redirect("/")

if __name__ == '__main__':
    session["error"] = ""
    app.run(debug=True)
