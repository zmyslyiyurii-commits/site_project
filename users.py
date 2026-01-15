from passlib.context import CryptContext
from database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, password: str):
    hashed = pwd_context.hash(password)

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def verify_user(email: str, password: str):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False

    return pwd_context.verify(password, row[0])
