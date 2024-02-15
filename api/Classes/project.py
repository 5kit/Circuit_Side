from .dbManager import Table
import json

class Project:
    def __init__(self, projectID=None, userID=None, Title=None, Circuit=None):
        self.projectID = projectID
        self.userID = userID
        self.Title = Title
        self.circuit = Circuit

    def to_json(self):
        json_data = {
            "ID" : self.projectID,
            "uID" : self.userID,
            "Title" : self.Title,
            "Circuit" : self.circuit,
        }
        return json.dumps(json_data)
    
    def from_json(self, json_data):
        # Load attributes from a JSON format.
        try:
            data = json.loads(json_data)
            self.projectID = data.get("ID", "")
            self.userID = data.get("uID", "")
            self.Title = data.get("Title", "")
            self.circuit = data.get("Circuit", "")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    def save(self):
        ProjDB.edit_entry({"Title" :  self.Title, 
                            "Circuit" : self.circuit}, 
                            f"projectID = '{self.projectID}'")
        print("Project saved successfully")
        return True

ProjDB = Table("Project")