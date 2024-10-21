import hashlib
import string
import random

characters = string.ascii_uppercase + string.ascii_lowercase + string.digits

random_key = ''.join(random.choices(characters, k=30))
input_password = "123456"
hashed_password = hashlib.sha256(random_key.encode() + input_password.encode()).hexdigest()

print("Random key : "+ random_key)
print("Hashed Password : "+ hashed_password)