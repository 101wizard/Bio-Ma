class Equipment:
    def __init__(self, e_id, e_name, e_img, e_amount, e_curr_amount):
        self.e_id = e_id  # INT
        self.e_name = e_name  # VARCHAR(255)
        self.e_img = e_img  # BLOB
        self.e_amount = e_amount  # INT
        self.e_curr_amount = e_curr_amount  # INT
