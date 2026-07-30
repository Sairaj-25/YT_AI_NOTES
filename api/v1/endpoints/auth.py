import hashlib
import hmac
import logging
import secrets
import time
from html import escape
from urllib.parse import urlencode

from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import get_db
from core.oauth import build_github_redirect_uri, github_oauth_configured, oauth
from schemas.db_schema import UserCreate, UserLogin
from services.auth_service import (
    authenticate_user,
    create_user,
    get_or_create_github_user,
)

settings = get_settings()
logger = logging.getLogger("YT_AI_NOTES")

router = APIRouter(prefix="/auth", tags=["auth"])


def auth_message_html(kind: str, title: str, detail: str) -> str:
    return f"""
            <div class="auth-response-message text-{kind}">
                <strong>{escape(title)}</strong> {escape(str(detail))}
            </div>
            """


# ---------------------------------------------------------------------------
# Stateless HMAC-signed state helpers (no session cookie required for CSRF)
# Root cause: browser drops session cookie after GitHub's cross-site redirect,
# so Authlib's session-based state lookup always returns None → MismatchingStateError.
# Solution: embed a self-verifiable HMAC signature inside the state param itself.
# ---------------------------------------------------------------------------


def make_state(secret: str) -> str:
    """Return a self-verifying state token: <nonce>.<timestamp>.<hmac>"""
    nonce = secrets.token_urlsafe(16)
    ts = str(int(time.time()))
    raw = f"{nonce}.{ts}"
    sig = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def verify_state(state: str, secret: str, max_age: int = 600) -> bool:
    """Verify the HMAC signature and that the token is not older than max_age seconds."""
    try:
        *parts, sig = state.split(".")
        raw = ".".join(parts)
        expected = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return False
        ts = int(parts[-1])
        return (int(time.time()) - ts) <= max_age
    except Exception:
        return False


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
        user = await create_user(db, user_data)
        request.session["user"] = {
            "email": user.email,
            "name": getattr(user, "name", None),
        }
        display_name = user.name or user.email
        return HTMLResponse(
            content=f"""
            {auth_message_html("success", "Account created:", f"Welcome, {display_name}! Redirecting...")}
            <script>setTimeout(() => {{ window.location.href = '/'; }}, 1500);</script>
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
        login_data = UserLogin(username=username, password=password)
        user = await authenticate_user(db, login_data)
        request.session["user"] = {
            "email": user.email,
            "name": getattr(user, "name", None),
        }
        display_name = user.name or user.email
        return HTMLResponse(
            content=f"""
            {auth_message_html("success", "Login successful:", f"Welcome back, {display_name}! Redirecting...")}
            <script>setTimeout(() => {{ window.location.href = '/'; }}, 1500);</script>
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


@router.get("/github/login")
async def github_login(request: Request):
    if not github_oauth_configured():
        raise HTTPException(status_code=500, detail="GitHub OAuth is not configured.")

    redirect_uri = build_github_redirect_uri(request, settings.GITHUB_CALLBACK_URL)
    state = make_state(settings.SESSION_SECRET_KEY)

    params = urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
    )
    auth_url = f"https://github.com/login/oauth/authorize?{params}"
    logger.info("Initiating GitHub OAuth with redirect_uri=%s", redirect_uri)
    return RedirectResponse(auth_url, status_code=302)


@router.get("/github/callback", name="github_callback")
async def github_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    try:
        # Check for OAuth errors from GitHub
        error = request.query_params.get("error")
        if error:
            raise OAuthError(
                error=error,
                description=request.query_params.get("error_description", error),
            )

        state = request.query_params.get("state", "")
        code = request.query_params.get("code", "")

        # Verify CSRF state — purely via HMAC, no session lookup required
        if not state or not verify_state(state, settings.SESSION_SECRET_KEY):
            raise OAuthError(
                error="invalid_state",
                description="OAuth state is invalid or has expired. Please try again.",
            )

        if not code:
            raise OAuthError(
                error="missing_code", description="No authorization code received."
            )

        redirect_uri = build_github_redirect_uri(request, settings.GITHUB_CALLBACK_URL)

        # Exchange authorization code for access token directly (bypasses session-based state)
        token = await oauth.github.fetch_access_token(
            code=code,
            redirect_uri=redirect_uri,
        )

        profile_response = await oauth.github.get("user", token=token)
        profile = profile_response.json()

        emails_response = await oauth.github.get("user/emails", token=token)
        emails = emails_response.json()

        user = await get_or_create_github_user(db, profile, emails)

        request.session["user"] = {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
            "auth_provider": user.auth_provider,
        }

        return RedirectResponse(url="/", status_code=303)

    except OAuthError as exc:
        logger.exception("GitHub OAuth callback failed: %s", exc)
        return HTMLResponse(
            content=auth_message_html(
                "danger",
                "GitHub login failed:",
                f"OAuth authorization was rejected or expired. {exc}",
            ),
            status_code=400,
        )

    except HTTPException as e:
        return HTMLResponse(
            content=auth_message_html("danger", "GitHub login failed:", e.detail),
            status_code=e.status_code,
        )
