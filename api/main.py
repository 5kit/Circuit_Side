from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
import pandas as pd
import json

from api.Classes.account import User

app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.config['SESSION_PERMANENT'] = True
Session(app)

# Reading CSV file into a DataFrame
df = pd.read_csv('Classes/component.csv')  

@app.route('/')
def home():
    error = session.get("error", "")
    # Rendering the home page with an optional error message
    return render_template('index.html', error_message=error)  

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        data = json.loads(user_json).get("projects")  # Extracting project data from user session
        Dc = df[['Code','Name']].to_dict(orient='index')  # Creating a dictionary for documentation
        return render_template('dashboard.html', username=usr.Username, projects=data, Docs=Dc)
    else:
        return redirect("/")  # Redirecting to the home page if user is not logged in

@app.route("/login", methods=["POST"])
def login():
    if request.method == "POST":
        username = request.form['login-username']
        password = request.form['login-password']
        user = User()
        # Attempting user login
        error = user.Login(username, password)  

        if user.LoggedIn:
            # Saving user details in session
            session["user"] = user.to_json()  
            return redirect("/dashboard")
        else:
            # Storing login error in session
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
            # Attempting user signup
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

@app.route("/create_project", methods=["POST"])
def CreateProject():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        usr.create_projects()
        # Saving user details after creating a project
        session["user"] = usr.to_json()  
        return redirect("/dashboard")
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
        # Redirecting to the home page if user is not logged in
        return redirect("/")  
    
@app.route('/settings', methods=['POST', 'GET'])
def settings():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        error = session.get("error", "")
        return render_template("settings.html", username=usr.Username, error_message=error) 
    else:
        # Redirecting to the home page if user is not logged in
        return redirect("/")  
    
@app.route('/change', methods=['POST'])
def Change():
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        type = request.form.get('val')
        if type == "name":
            # Attempting to edit the username
            newName = request.form.get('new_name')
            session["error"] = usr.edit_Name(newName)  
            session["user"] = usr.to_json()  
            return redirect("/settings")
        elif type == "pass":
            Pass_old = request.form.get('old_pass')
            Pass_new1 = request.form.get('new1_pass')
            Pass_new2 = request.form.get('new2_pass')
            if Pass_new1 == Pass_new2:
                # Attempting to edit the password
                session["error"] = usr.edit_Pass(Pass_old, Pass_new1)  
                session["user"] = usr.to_json()  
                return redirect("/settings")
            else:
                # Handling mismatched passwords
                session["error"] = "Passwords dont match." 
    # Redirecting to the settings if unsuccessful
    return redirect("/settings")


@app.route('/search', methods=['POST', 'GET'])
def search():
    # Check if user is logged in
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        # Handle POST request (form submission)
        if request.method == 'POST':
            # Perform search based on the query
            query = request.form.get("search")
            data = usr.search_projects(query)
        # Handle GET request (initial page load)
        elif request.method == 'GET':
            query = ""
            data = {}
        # Render the search.html template with relevant data
        return render_template("search.html", username=usr.Username, query=query, results=data)
    # Redirect to home page if user is not logged in
    return redirect("/")
    
@app.route('/documentation', methods=["POST"])
def document():
    # Extracting documentation details
    id = request.form.get("comp_id")
    Dc = list(df[df['Code'] == id].to_dict(orient='index').values())[0]  
    return render_template("document.html", name=Dc["Name"], info=Dc["Description"])

@app.route("/logout", methods=["POST"])
def logout():
    # Logging out the user by removing user details from session
    session.pop("user", None)  
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
