import random
import string

def generate_random_characters(length=30):
    # Combine uppercase letters and digits
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    # Generate a random selection of the combined characters
    random_characters = ''.join(random.choices(characters, k=length))
    return random_characters

# Generate and print 30 random characters
random_string = generate_random_characters()
print(random_string)