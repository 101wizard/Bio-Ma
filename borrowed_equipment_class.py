class BorrowedEquipment:
    def __init__(self, borrow_id, e_id, amount, due_date):
        self.borrow_id = borrow_id  # INT (Foreign Key referencing Borrow)
        self.e_id = e_id  # INT (Foreign Key referencing Equipment)
        self.amount = amount  # INT
        self.due_date = due_date  # DATETIME
