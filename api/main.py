from flask import Flask, render_template, request, redirect, url_for, session, make_response
from api.Classes.account import User
import os

app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)
usr = User()
error = ""


@app.route('/')
def home():
    if usr.LoggedIn:
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html', error_message=error)

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

@app.route('/dashboard')
def dashboard():
    if usr.LoggedIn:
        return render_template('dashboard.html', username=usr.Username)
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['POST'])
def login():
    global error
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']

        error = usr.Login(username, password)
        if usr.LoggedIn:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('home'))
    
@app.route('/signup', methods=['POST'])
def signup():
    global error
    if request.method == 'POST':
        username = request.form['signup-username']
        password = request.form['signup-password']
        confirm = request.form['confirm-password']
        
        if password == confirm:
            error = usr.signUp(username, password)
        else:
            error = "Passwords dont match"
        if usr.LoggedIn:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('home'))
    
@app.route('/logout', methods=['POST'])
def logout():
    usr.Logout()
    session.clear()

    response = make_response(redirect(url_for('home')))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    return response

if __name__ == '__main__':
    app.run(debug=True)