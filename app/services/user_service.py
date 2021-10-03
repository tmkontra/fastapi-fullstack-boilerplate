from passlib.context import CryptContext


crypt = CryptContext(["bcrypt"], deprecated="auto")


def hash_password(plain_text):
    return crypt.hash(plain_text)


def verify_password(plain_password, hashed_password):
    return crypt.verify(plain_password, hashed_password)
