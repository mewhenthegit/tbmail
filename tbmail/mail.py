class Mail:
    def __init__(self, idx, sender, receiver, body, read):
        self.idx = idx
        self.sender = sender
        self.receiver = receiver
        self.body = body
        self.read = read 

    def serialize(self):
        return self.idx, {
            "sender": self.sender,
            "receiver": self.receiver,
            "body": self.body,
            "read": self.read
        }
    
    def deserialize(idx, data):
        return Mail(idx, data["sender"], data["receiver"], data["body"], data["read"])
    
    def search(db, sender=None, receiver=None, read=None, count=0):
        db.load()
        results = []
        for idx, mail in enumerate(db.data["mails"]):
            if count and len(results) == count:
                return results

            if sender and not mail["sender"] == sender:
                continue 

            if receiver and not mail["receiver"] == receiver:
                continue

            if read and not mail["read"] == read:
                continue
            
            results.append(Mail.deserialize(idx, mail))
        
        return results
