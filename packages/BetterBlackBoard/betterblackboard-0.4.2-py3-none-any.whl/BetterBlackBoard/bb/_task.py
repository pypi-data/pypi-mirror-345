import datetime

class Task:
    def __init__(self, title: str, submission: bool, deadline: datetime.datetime = None):
        self.title = title
        self.submission = submission
        self.deadline = deadline

    def __repr__(self):
        return self.title
    
    def __lt__(self, other):
        if self.deadline == None:
            return False
        elif other.deadline == None:
            return True
        else:
            return self.deadline < other.deadline
