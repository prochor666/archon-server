import secrets
import random
import string
import hashlib


def token_urlsafe(nbytes: int = 64) -> str:
    return secrets.token_urlsafe(nbytes)


def token_bytes(nbytes: int = 64) -> str:
    return str(secrets.token_bytes(nbytes))


def token_rand(length: int = 64) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    t = ''.join(random.choice(chars) for i in range(length))
    return t


def pin(length: int = 6) -> str:
    chars = string.digits
    t = ''.join(random.choice(chars) for i in range(length))
    return t


def create_secret(blck_items: dict = {}) -> str | bool:
    if type(blck_items) is dict and len(blck_items.keys()) > 0:
        gen = hashlib.blake2b()

        for key, blck in blck_items.items():
            gen.update(blck.encode('utf-8'))

        secret_blck = gen.hexdigest()

        return secret_blck

    return False
