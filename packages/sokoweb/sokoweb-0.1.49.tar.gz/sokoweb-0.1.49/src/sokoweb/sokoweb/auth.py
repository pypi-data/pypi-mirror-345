# auth.py

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
import os
from dotenv import load_dotenv
from sqlalchemy.future import select

from .database import async_session
from .db_models import User as DBUser
from .models import TokenData

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "products:read": "Read products",
        "products:write": "Write products",
        "credits:manage": "Manage credits",
        "categories:read": "Read categories",
        "categories:write": "Write categories",
    },
)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str) -> Optional[DBUser]:
    async with async_session() as session:
        result = await session.execute(select(DBUser).where(DBUser.username == username))
        user = result.scalar_one_or_none()
        return user

async def authenticate_user(username: str, password: str) -> Optional[DBUser]:
    user = await get_user(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)
) -> DBUser:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
    user = await get_user(token_data.username)
    if user is None:
        raise credentials_exception
    user_scopes = user.scopes.split(',') if user.scopes else []
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes or scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user

async def add_credits_to_user(username: str, amount: float) -> None:
    async with async_session() as session:
        result = await session.execute(select(DBUser).where(DBUser.username == username))
        user = result.scalar_one_or_none()
        if user:
            user.credits += amount
            session.add(user)
            await session.commit()

async def deduct_credits_from_user(username: str, amount: float) -> bool:
    async with async_session() as session:
        result = await session.execute(select(DBUser).where(DBUser.username == username))
        user = result.scalar_one_or_none()
        if user and user.credits >= amount:
            user.credits -= amount
            session.add(user)
            await session.commit()
            return True
        return False

async def get_user_credits(username: str) -> float:
    async with async_session() as session:
        result = await session.execute(select(DBUser.credits).where(DBUser.username == username))
        credits = result.scalar_one_or_none()
        return credits if credits is not None else 0.0

if __name__ == "__main__":
    print(get_password_hash("password"))