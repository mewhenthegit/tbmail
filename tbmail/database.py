from pathlib import Path
import json
DATABASE = Path(__file__).parents[1] / "db.json"

class Database:
    def __init__(self):
        self.data = {}
        self.load()

    def write(self):
        with open(DATABASE, "w") as f:
            f.write(json.dumps(self.data))
    
    def load(self):
        if not DATABASE.is_file():
            with open(DATABASE, "w+") as f:
                self.data = {"users": [], "mails": [], "linkcodes": {}, "recovercodes": {}}
                f.write(json.dumps(self.data))
        
        else:
            with open(DATABASE, "r") as f:
                self.data = json.loads(f.read())