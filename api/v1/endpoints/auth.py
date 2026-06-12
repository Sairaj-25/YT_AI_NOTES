from html import escape

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from schemas.db_schema import UserCreate, UserLogin
from services.auth_service import create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


def auth_message_html(kind: str, title: str, detail: str) -> str:
    return f"""
            <div class="auth-response-message text-{kind}">
                <strong>{escape(title)}</strong> {escape(str(detail))}
            </div>
            """


@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_data = UserCreate(name=name, email=email, password=password)

        # create user in DB
        user = await create_user(db, user_data)

        # Store user in session
        request.session["user"] = {
            "email": user.email,
            "name": getattr(user, "name", None),
        }

        # Success response with redirect
        display_name = user.name or user.email
        return HTMLResponse(
            content=f"""
            {auth_message_html(
                "success",
                "Account created:",
                f"Welcome, {display_name}! Redirecting...",
            )}
            <script>
                setTimeout(() => {{
                window.location.href = '/';
                }}, 1500);
            </script>
            """,
            status_code=200,
        )

    except HTTPException as e:
        return HTMLResponse(
            content=auth_message_html("danger", "Registration failed:", e.detail),
            status_code=e.status_code,
        )


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        login_data = UserLogin(
            username=username,
            password=password,
        )

        user = await authenticate_user(db, login_data)

        request.session["user"] = {
            "email": user.email,
            "name": getattr(user, "name", None),
        }
        display_name = user.name or user.email
        return HTMLResponse(
            content=f"""
            {auth_message_html(
                "success",
                "Login successful:",
                f"Welcome back, {display_name}! Redirecting...",
            )}
            <script>
                setTimeout(() => {{
                window.location.href = '/';
                }}, 1500);
            </script>
            """,
            status_code=200,
        )

    except HTTPException:
        return HTMLResponse(
            content=auth_message_html(
                "danger", "Login failed:", "Invalid email or password."
            ),
            status_code=401,
        )

    except Exception:
        return HTMLResponse(
            content=auth_message_html("danger", "Login failed:", "Please try again."),
            status_code=400,
        )
