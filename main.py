from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from users import create_user, verify_user, users_db

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if verify_user(email, password):
        return templates.TemplateResponse("profile.html", {"request": request, "email": email})
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неправильний email або пароль"})

@app.post("/signup", response_class=HTMLResponse)
def signup(request: Request, email: str = Form(...), password: str = Form(...)):
    if any(u["email"] == email for u in users_db):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Користувач вже існує"})
    create_user(email, password)
    return templates.TemplateResponse("login.html", {"request": request, "message": "Користувача створено! Тепер увійдіть."})
