import hashlib
from .dbManager import Table
from .project import Project
import json


# Hash algorithm
def Hash256(data):
    if isinstance(data, str):
        data = data.encode()
    sha256_hash = hashlib.sha256(data).hexdigest()
    return sha256_hash


class User:
    def __init__(self):
        # Set to a logged out state
        self.__ID = ""
        self.Username = ""
        self.LoggedIn = False
        self.projects = []
        
    def to_json(self):
        # Serialize the object's attributes to JSON format.
        user_json = {
            "ID": self.__ID,
            "Username": self.Username,
            "LoggedIn": self.LoggedIn,
            "projects": {n : self.projects[n].to_json() for n in range(len(self.projects))}
        }
        return json.dumps(user_json)

    def from_json(self, json_data):
        # Load attributes from a JSON format.
        try:
            user_data = json.loads(json_data)
            self.__ID = user_data.get("ID", "")
            self.Username = user_data.get("Username", "")
            self.LoggedIn = user_data.get("LoggedIn", False)
            self.load_projects()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def Login(self, username, password):
        if not self.LoggedIn:
            # Query the database to check if the username exists
            user_data = AccDB.query("*", f"Username = '{username.lower()}'")

            # Extract account details from
            if user_data:
                user_data = user_data[0]
                stored_password = user_data["Password"]

                if Hash256(password) == stored_password:
                    # Set object to a logged in state
                    self.Username = user_data["Username"]
                    self.__ID = user_data["userID"]
                    self.LoggedIn = True
                    self.load_projects()
                    return ""

            return "Password or Username are incorrect"
        else:
            return "Already logged in."

    def signUp(self, new_name, new_pass):
        # Check username and password validity
        if len(new_name) >= 4 and len(new_name) <= 12:
            if len(new_pass) >= 5 and len(new_pass) <= 12:
                if new_name.lower() not in [
                    user["Username"].lower()
                    for user in AccDB.query("*", f"Username = '{new_name.lower()}'")
                ]:
                    # Create a unique ID for database entry
                    q = AccDB.query("userID", None, "userID DESC")
                    if q:
                        num = int(q[0]["userID"][1:]) + 1
                        Pid = "U{0:03d}".format(num)
                    else:
                        Pid = "U000"

                    # Add the new user to the database
                    AccDB.add_entry(
                        {
                            "userID": Pid,
                            "Username": new_name.lower(),
                            "Password": Hash256(new_pass),
                        }
                    )

                    # Log in the new user
                    self.Login(new_name, new_pass)
                    return ""
                else:
                    return "Username is already taken."
            else:
                return "Password should be within 5-12 characters."
        else:
            return "Username should be within 4-12 characters."
    
    def edit_Name(self, new_name):
        if self.LoggedIn:
            # Verify new username and change entry
            if len(new_name) >= 4 and len(new_name) <= 12:
                if new_name.lower() not in [
                    user["Username"].lower()
                    for user in AccDB.query("*", f"Username = '{new_name.lower()}'")
                ]:
                    AccDB.edit_entry({"Username" : new_name}, f"userID = '{self.__ID}'")
                    self.Username = new_name
                    return ""
                else:
                    return "Username is already taken."
            else:
                return "Username should be within 4-12 characters."
        return "Not logged in!"
    
    def edit_Pass(self, old_pass, new_pass):
        if self.LoggedIn:
            # Verify old password
            psw_hash = AccDB.query("Password", f"userID = '{self.__ID}'")[0]["Password"]
            if Hash256(old_pass) != psw_hash:
                return "Incorrect password!"
                
            # Verify new password and change entry
            if len(new_pass) >= 5 and len(new_pass) <= 12:
                AccDB.edit_entry({"Password" : Hash256(new_pass)}, f"userID = '{self.__ID}'")
                return ""
            else:
                return "Password should be within 5-12 characters."

    def create_projects(self, title=None):
        # Check for duplicate project title
        for i in self.projects:
            if i.Title == title:
                return "title taken"
        # Create a unique ID for database entry
        q = ProjDB.query("projectID", None, "projectID DESC")
        if q != ():
            num = int(q[0]["projectID"][1:]) + 1
            Pid = "P{0:04d}".format(num)
        else:
            Pid = "P0000"
            
        if title == None:
            title = "Project" + str(len(self.projects) + 1)

        # Insert into database
        ProjDB.add_entry(
            {"projectID": Pid, 
            "userID": self.__ID, 
            "Title": title, 
            "Circuit": "" })

        self.projects.append(Project(Pid, self.__ID, title, ""))
        return ""

    def delete_project(self, index):
        if self.LoggedIn:
            # Get id and remove entry
            Pid = self.projects[index].projectID
            ProjDB.remove_entry(f"projectID = '{Pid}'")
            self.projects.pop(index)
            return ""
        else:
            return "Not logged in!"

    def load_projects(self):
        if self.LoggedIn:
            self.projects = []
            # Iterate for every project the user has
            query = ProjDB.query("*", f"userID = '{self.__ID}'")
            for p in query:
                dat = tuple(p.values())
                self.projects.append(Project(dat[0], dat[1], dat[2], dat[3]))
            return ""
        else:
            return "Not logged in!"

    def Logout(self):
        if self.LoggedIn:
            # Set to a logged out state
            self.__ID = ""
            self.Username = ""
            self.LoggedIn = False
            return ""
        else:
            return "Not logged in!"

    def Delete_account(self):
        if self.LoggedIn:
            # Maintain referential integrity
            ProjDB.remove_entry(f"userID = '{self.__ID}'")
            AccDB.remove_entry(f"userID = '{self.__ID}'")
            self.Logout()
            return "Account Successfully Removed!"
        else:
            return "Not logged in!"


# Initialise Table mangers
AccDB = Table("Account")
ProjDB = Table("Project")