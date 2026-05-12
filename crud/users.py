from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hashlib import sha256
import secrets
from datetime import datetime, timedelta
from models.users import User, UserToken
from schemas.users import UserCreate

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(db_user)
    await db.flush()
    await db.refresh(db_user)
    return db_user

async def create_user_token(db: AsyncSession, user_id: int):
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_token = UserToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    await db.flush()
    await db.refresh(db_token)
    
    return token
