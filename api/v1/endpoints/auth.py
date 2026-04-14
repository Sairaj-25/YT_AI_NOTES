from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

from schemas.db_schema import UserCreate, UserLogin
from services.auth_service import create_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_data = UserCreate(
            name=name,
            email=email,
            password=password
        )

        # create user in DB
        user = await create_user(db, user_data)

        # Store user in session
        request.session["user"] = {
            "email": user.email,
            "name": getattr(user, "name", None),
        }

        # Success response with redirect
        return HTMLResponse(
            content=f"""
            <div class="text-success" style="font-size: 0.9rem; text-align: center;">
                Account created successfully from {user.name or user.email}! Redirecting...
            </div>
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
            content=f'<div class="text-danger">{e.detail}</div>',
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
        return HTMLResponse(
            content=f"""
            <div class="text-success" style="font-size: 0.9rem; text-align: center;">
                Login successful ! welcome back {user.name or user.email}! Redirecting...
            </div>
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
            content=f"""
            <div class="text-danger">Invalid email or password.</div>
            <script>
                document.querySelectorAll('.sf-input').forEach(el => el.classList.add('error-field'));
            </script>
            """,
            status_code=401,
        )
    
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <div class="text-danger" style="font-size: 0.9rem; text-align: center;">
                Login failed: {str(e)}
            </div>
            <script>
                document.querySelectorAll('.sf-input').forEach(el => el.classList.add('error-field'));
                </script>""",
            status_code=400,
        )