from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from hashlib import sha256
import secrets
from datetime import datetime, timedelta
from models.users import User, UserToken
from schemas.users import UserCreate, UserUpdate

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

async def verify_user_password(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    
    if user.password == hash_password(password):
        return user
    return None

async def get_valid_token(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(UserToken).where(
            UserToken.user_id == user_id,
            UserToken.expires_at > datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()

async def get_token_by_value(db: AsyncSession, token: str):
    result = await db.execute(
        select(UserToken).where(
            UserToken.token == token,
            UserToken.expires_at > datetime.utcnow()
        )
    )
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def update_user(db: AsyncSession, user_id: int, update_data: UserUpdate):
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    
    for key, value in update_dict.items():
        if value is not None:
            setattr(user, key, value)
    
    await db.flush()
    await db.refresh(user)
    return user

async def update_user_password(db: AsyncSession, user_id: int, old_password: str, new_password: str):
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    if user.password != hash_password(old_password):
        return False
    
    user.password = hash_password(new_password)
    await db.flush()
    return True
