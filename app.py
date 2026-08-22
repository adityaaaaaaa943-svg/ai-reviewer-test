import sqlite3

API_KEY = "sk-test-1234567890abcdef"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()


def do_everything(data):
    validated = data.strip()
    conn = sqlite3.connect("users.db")
    conn.execute("INSERT INTO logs VALUES (?)", (validated,))
    result = get_user(validated)
    print(result)
    return result