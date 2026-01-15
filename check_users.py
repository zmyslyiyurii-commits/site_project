import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT id, email FROM users")
users = cursor.fetchall()

print("Users in DB:")
for u in users:
    print(u)

conn.close()
