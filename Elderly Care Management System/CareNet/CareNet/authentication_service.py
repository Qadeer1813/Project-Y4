from .app import get_db_connection
from .functions import hash_password

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Password, role FROM users WHERE Username = %s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def create_user(username, raw_password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    hashed = hash_password(raw_password)
    cursor.execute(
        "INSERT INTO users (Username, Password, role) VALUES (%s, %s, %s)",
        (username, hashed, role)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True