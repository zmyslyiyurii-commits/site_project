from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
users_db = []

def create_user(email: str, password: str) -> dict:
    hashed_password = pwd_context.hash(password[:72])  # bcrypt обмеження 72 байти
    user = {"email": email, "hashed_password": hashed_password}
    users_db.append(user)
    return user

def verify_user(email: str, password: str) -> bool:
    user = next((u for u in users_db if u["email"] == email), None)
    if not user:
        return False
    return pwd_context.verify(password, user["hashed_password"])
