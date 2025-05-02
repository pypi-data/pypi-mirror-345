import random
import string

word_list = [
    "dragon", "apple", "sunset", "river", "cloud", "forest", "ocean",
    "mountain", "star", "planet", "shadow", "wolf"
]

def simple_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def secure_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def memorable_password(num_words=3):
    return '-'.join(random.choice(word_list) for _ in range(num_words))

def passphrase(num_words=5):
    return ' '.join(random.choice(word_list) for _ in range(num_words))
