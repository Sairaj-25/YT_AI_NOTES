from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.db_models import User
from schemas.db_schema import UserCreate, UserLogin

# password hashing config
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password for secure storage"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """Create a new user in the database
    Raises HTTPException if email already exists
    """

    # check if user already exists
    filter_user = select(User).where(User.email == user.email)
    await_result = await db.execute(filter_user)
    existing_user = await_result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash Password
    hashed_pwd = hash_password(user.password)

    # Create DB user object (SQLAlchemy model)
    db_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
    )

    # save to DB
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def authenticate_user(db: AsyncSession, login: UserLogin) -> User:
    filter_user = select(User).filter(User.email == login.username)
    await_result = await db.execute(filter_user)
    result = await_result.scalars().first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Merge the object into the session to ensure attributes are loaded
    user = await db.merge(result)

    # verify password
    if not user.password or not verify_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return user


def pick_github_email(profile: dict, emails: list[dict]) -> str:
    if profile.get("email"):
        return profile["email"]

    for email in emails:
        if email.get("primary") and email.get("verified"):
            return email["email"]

    for email in emails:
        if email.get("verified"):
            return email["email"]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="GitHub account has no verified email address.",
    )


async def get_or_create_github_user(
    db: AsyncSession,
    profile: dict,
    emails: list[dict],
) -> User:
    github_id = str(profile["id"])
    email = pick_github_email(profile, emails)
    name = profile.get("name") or profile.get("login") or email.split("@")[0]
    avatar_url = profile.get("avatar_url")

    result = await db.execute(select(User).where(User.github_id == github_id))
    user = result.scalars().first()

    if user:
        user.email = email
        user.name = name
        user.avatar_url = avatar_url
        user.auth_provider = user.auth_provider or "github"
        await db.commit()
        await db.refresh(user)
        return user

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user:
        user.github_id = github_id
        user.avatar_url = avatar_url
        user.auth_provider = user.auth_provider or "local"
        await db.commit()
        await db.refresh(user)
        return user

    user = User(
        name=name,
        email=email,
        password=None,
        github_id=github_id,
        avatar_url=avatar_url,
        auth_provider="github",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user
