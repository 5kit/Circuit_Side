from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
import redis
from dotenv import load_dotenv
import os
import pandas as pd
import json

from api.Classes.account import User
from api.Classes.project import Project
from api.Classes.editor import Open

load_dotenv()

app = Flask(__name__)

# Configure Redis connection
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Set secret key for Flask session
app.secret_key = 'w978r-hbfrw7-3gf9e7s-9gfsdh'

# Configure Flask-Session to use Redis
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

# Initialize Flask-Session
Session(app)

# Reading CSV file into a DataFrame
df = pd.read_csv('api/Classes/component.csv')  

@app.route('/')
def home():
    session["Project"] = ""
    error = session.get("error", "")
    # Rendering the home page with an optional error message
    return render_template('index.html', error_message=error)  

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user_json = session.get("user")
    if user_json:
        session["Project"] = ""
        usr = User()
        usr.from_json(user_json)
        data = usr.projects
        Projs = {}
        if data:
            for i in range(len(data)):
                Projs[str(i)] = json.loads(data[i].to_json())
        Dc = df[['Code','Name']].to_dict(orient='index')  # Creating a dictionary for documentation
        return render_template('dashboard.html', username=usr.Username, projects=Projs, Docs=Dc)
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
        # Gathering the user input
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
            # Successful signup
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
        # Automatically create a Project name
        newTitle = "Project" + str(len(usr.projects))
        usr.create_projects(newTitle)
        # Saving user details after creating a project
        session["user"] = usr.to_json()  
        return redirect("/dashboard")
    else:
        return redirect("/")
    
@app.route("/delete_project", methods=["POST"])
def DeleteProject():
    n = int(request.form.get('project_id'))
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        # Remove project and update user session
        usr.delete_project(n)
        session["user"] = usr.to_json()  
        return redirect("/dashboard")
    else:
        # Redirecting to the home page if user is not logged in
        return redirect("/")  

@app.route('/editor')
def editor():
    user_json = session.get("user")
    prj_json = session.get("Project")
    if user_json:
        if prj_json:
            Prj = Project()
            Prj.from_json(prj_json)
            error = session.get("error", "")
            return render_template("editor.html", error_message=error ,Title=Prj.Title)
        else:
            return redirect("/dashboard")
    else:
        # Redirecting to the home page if user is not logged in  
        return redirect("/")

@app.route('/open_edit', methods=['POST'])
def open_edit():
    n = int(request.form.get('project_id'))
    user_json = session.get("user")
    if user_json:
        usr = User()
        usr.from_json(user_json)
        usr.load_projects()
        session["Project"] = usr.projects[n].to_json()
        return redirect("/editor")
    else:
        # Redirecting to the home page if user is not logged in
        return redirect("/")
    
@app.route('/change_Title', methods=['POST'])
def Change_Title():
    prj_json = session.get("Project")
    user_json = session.get("user")
    newTitle = request.form.get('nTitle')
    if user_json:
        if prj_json and newTitle:
            usr = User()
            usr.from_json(user_json)
            Prj = Project()
            Prj.from_json(prj_json)
            Prj.Title = newTitle
            e = usr.check_title(newTitle)
            if e:
                session["error"] = e
            else:
                session["Project"] = Prj.to_json()
            return redirect("/editor")
        else:
            return redirect("/dashboard")
    else:
        return redirect("/")

@app.route('/edit', methods=['POST'])
def edit():
    user_json = session.get("user")
    prj_json = session.get("Project")
    if user_json:
        if prj_json:
            usr = User()
            usr.from_json(user_json)
            Prj = Project()
            Prj.from_json(prj_json)
            newCircuit = Open(Prj.circuit)
            Prj.circuit = newCircuit
            session["Project"] = Prj.to_json()
            return redirect("/editor")
        else:
            return redirect("/dashboard")
    else:
        return redirect("/")
        
    
@app.route('/save', methods=['POST'])
def Save_project():
    prj_json = session.get("Project", "")
    user_json = session.get("user")
    if user_json:
        if prj_json:
            Prj = Project()
            Prj.from_json(prj_json)
            Prj.save()
            usr = User()
            usr.from_json(user_json)
        return redirect("/dashboard")
    else:
        return redirect("/")
    
@app.route('/settings', methods=['POST', 'GET'])
def settings():
    session["Project"] = ""
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
        elif type == 'remAcc':
            usr.Delete_account()
            session["error"] = "Account deleted successfully"
            session.pop("user", None) 
            session.pop("Project", None) 
            return redirect('/')
    # Redirecting to the settings if unsuccessful
    return redirect("/settings")


@app.route('/search', methods=['POST', 'GET'])
def search():
    session["Project"] = ""
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
    session.pop("Project", None)  
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
