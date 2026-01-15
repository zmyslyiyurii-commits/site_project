import sqlite3

DB_NAME = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


# import sqlite3
# from passlib.context import CryptContext

# # Хешування паролів
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # Підключення до бази (файл створиться автоматично)
# DB_NAME = "users.db"

# def get_db_connection():
#     """Повертає підключення до SQLite бази"""
#     conn = sqlite3.connect(DB_NAME, check_same_thread=False)
#     return conn

# def init_db():
#     """Створює таблицю users, якщо її ще немає"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             email TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL
#         )
#     """)
#     conn.commit()
#     conn.close()

# # Викликаємо ініціалізацію бази одразу при імпорті
# init_db()

# # Функції для роботи з користувачами
# def create_user(email: str, password: str) -> bool:
#     """Створює нового користувача в базі. Повертає True якщо успішно, False якщо email існує"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     hashed_password = pwd_context.hash(password)
#     try:
#         cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         # Таке вже є в базі
#         return False
#     finally:
#         conn.close()

# def verify_user(email: str, password: str) -> bool:
#     """Перевіряє логін та пароль користувача"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
#     row = cursor.fetchone()
#     conn.close()
#     if row:
#         hashed_password = row[0]
#         return pwd_context.verify(password, hashed_password)
#     return False

# def list_users():
#     """Повертає список всіх користувачів (id та email)"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, email FROM users")
#     users = cursor.fetchall()
#     conn.close()
#     return [{"id": u[0], "email": u[1]} for u in users]
