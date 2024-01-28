import random
import string


def generate_random_string():
    allowed_characters = string.ascii_letters + string.digits + '_-'
    return ''.join(random.choice(allowed_characters) for _ in range(32))
