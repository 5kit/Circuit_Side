from .dbManager import Table

class Project:
    def __init__(self, projectID, userID, Title, Circuit):
        self.projectID = projectID
        self.userID = userID
        self.Title = Title
        self.circuit = Circuit

    def save(self):
        ProjDB.edit_entry({"Title" :  self.Title, 
                            "Circuit" : self.circuit}, 
                            f"projectID = '{self.projectID}'")
        print("Project saved successfully")
        return True

ProjDB = Table("Project")