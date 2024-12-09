class User:
    def __init__(self, idx, username, password, welcoming, home):
        self.idx = idx
        self.username = username
        self.password = password # bcrypt hashed and salted
        self.welcoming = welcoming
        self.home = home
    
    def serialize(self):
        return self.idx, {
            # "id": self.id,
            "username": self.username,
            "password": self.password,
            "home": self.home,
            "welcoming": self.welcoming
        }
    
    def deserialize(idx, data):
        return User(idx, data["username"], data["password"], data["welcoming"], data["home"])
    
    def search(db, id=None, username=None, home=None):
        db.load()
        for idx, user in enumerate(db.data["users"]):
            if id and not user["id"] == id:
                continue
            
            if username and not user["username"] == username:
                continue

            if home and not user["home"] == home:
                continue 

            return User.deserialize(idx, user)