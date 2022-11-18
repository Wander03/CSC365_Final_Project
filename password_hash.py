import os
import hashlib
from base64 import b64encode

# how to create hash and salt for password and get hash (delete once Dylan sees how)

def create_hash(password):
    salt = os.urandom(32)  # A new salt for this user
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    return key, salt


def get_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),  # Convert the password to bytes
        salt,
        100000
    )
