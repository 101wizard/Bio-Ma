class Researcher:
    def __init__(self, r_id, r_name, r_phone, r_email, r_img):
        self.r_id = r_id  # INT
        self.r_name = r_name  # VARCHAR(255)
        self.r_phone = r_phone  # VARCHAR(15)
        self.r_email = r_email  # VARCHAR(255)
        self.r_img = r_img  # BLOB