class Borrow:
    def __init__(self, borrow_id, r_id, la_id, borrow_date):
        self.borrow_id = borrow_id  # INT
        self.r_id = r_id  # INT (Foreign Key referencing Researcher)
        self.la_id = la_id  # INT (Foreign Key referencing LabAssistant)
        self.borrow_date = borrow_date  # DATETIME
