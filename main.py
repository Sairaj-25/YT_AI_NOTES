import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from core.database import engine, Base
from contextlib import asynccontextmanager
from api.v1.endpoints.auth import router


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("YT_AI_NOTES")


# create a lifespan function to handle DB initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    # this runs when the app starts
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Anything after yield runs when app shuts down


# APP
app = FastAPI(
    title="YT_AI_NOTES API",
    description="AI-powered Notes creation",
    lifespan=lifespan,
)


# Sessions (cockie-based)
app.add_middleware(
    SessionMiddleware,
    secret_key="change-me-in-production",
    same_site="lax",
    https_only=False,
)


# main.py path
BASE_DIR = Path(__file__).resolve().parent

# static files
app.mount(
    "/static/",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)

# templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Router
app.include_router(router, prefix="/api/v1")

# Frontend Route


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(request, "index.html", {"user": user})


@app.get("/login", response_class=HTMLResponse, name="signin_page")
async def login_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(request, "signin.html", {"user": user})


@app.get("/register", response_class=HTMLResponse, name="signup_page")
async def register_page(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse(request, "signup.html", {"user": user})


@app.get("/logout", name="logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
