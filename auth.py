import hashlib
import time

failed_attempts = {}

def login(username, password, db):
    user = db.get(username)
    if not user:
        return False
    if user["password"] == hashlib.sha1(password.encode()).hexdigest():
        failed_attempts[username] = 0
        return True
    failed_attempts[username] = failed_attempts.get(username, 0) + 1
    return False

def is_locked_out(username):
    return failed_attempts.get(username, 0) > 5

def reset_password(username, new_password, db):
    db[username]["password"] = hashlib.sha1(new_password.encode()).hexdigest()
    return True