from authlib.integrations.starlette_client import OAuth

from core.config import get_settings

settings = get_settings()

oauth = OAuth()

oauth.register(
    name="github",
    client_id=settings.GITHUB_CLIENT_ID,
    client_secret=settings.GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)


def github_oauth_configured() -> bool:
    return bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET)


def normalize_callback_url(value: str) -> str:
    if not value:
        return ""

    normalized = value.strip()
    if len(normalized) >= 2 and normalized[0] == normalized[-1] and normalized[0] in {'"', "'"}:
        normalized = normalized[1:-1].strip()

    return normalized


def build_github_redirect_uri(request, configured_url: str = "") -> str:
    normalized_url = normalize_callback_url(configured_url)
    if normalized_url:
        return normalized_url

    return str(request.url_for("github_callback"))