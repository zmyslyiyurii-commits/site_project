from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
import sqlite3
from database import get_db_connection, init_db

from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image, ImageEnhance
import io

app = FastAPI()

# ===== MIDDLEWARE =====
app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY_CHANGE_ME"
)

# ===== STATIC + TEMPLATES =====
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===== INIT DB =====
init_db()

# ===== OAUTH =====
oauth = OAuth()
oauth.register(
    name="google",
    client_id="PASTE_CLIENT_ID_FROM_GOOGLE",
    client_secret="PASTE_CLIENT_SECRET_FROM_GOOGLE",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# ===================== ROUTES =====================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email=?", (email,))
    row = cursor.fetchone()
    conn.close()

    if not row or row[0] != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": {}, "error": "Неправильний логін або пароль"}
        )

    response = RedirectResponse("/profile", status_code=302)
    response.set_cookie("user_email", email)
    return response


@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return templates.TemplateResponse(
            "signup.html",
            {"request": {}, "error": "Користувач вже існує"}
        )

    conn.close()
    return RedirectResponse("/", status_code=302)


@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/")
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "email": email}
    )


@app.get("/logout")
def logout():
    response = RedirectResponse("/")
    response.delete_cookie("user_email")
    return response


# ================= GOOGLE AUTH =================

@app.get("/login/google")
async def login_google(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]

    email = user["email"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)",
        (email, "google")
    )
    conn.commit()
    conn.close()

    response = RedirectResponse("/profile")
    response.set_cookie("user_email", email)
    return response

@app.get("/editor", response_class=HTMLResponse)
def photo_editor(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        return RedirectResponse("/")
    return templates.TemplateResponse("photo_editor.html", {"request": request, "email": email})

@app.post("/editor/upload")
async def upload_image(file: UploadFile = File(...)):
    # Відкриваємо фото через Pillow
    image = Image.open(file.file).convert("RGB")
    
    # Простий приклад: змінюємо розмір та яскравість
    image = image.resize((400, 400))
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.2)  # трохи яскравіше

    # Зберігаємо у байтовий потік
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return StreamingResponse(img_bytes, media_type="image/png")
