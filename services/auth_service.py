from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.db_models import User
from schemas.db_schema import UserCreate, UserLogin

# password hashing config
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """ Hash a password for secure storage"""
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
    db_user =User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
    )

    # save to DB
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user

async def authenticate_user(db:AsyncSession, login: UserLogin) -> User:
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
    if not verify_password(login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return user

