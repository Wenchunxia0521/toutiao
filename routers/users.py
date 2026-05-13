from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from schemas.users import UserCreate, UserLogin, UserUpdate, PasswordUpdate
from crud.users import get_user_by_username, create_user, create_user_token, verify_user_password, get_valid_token, \
    get_token_by_value, get_user_by_id, update_user, update_user_password as update_password
from config.db_conf import get_db


async def get_current_user(
        authorization: Optional[str] = Header(None),
        db: AsyncSession = Depends(get_db)
):
    if not authorization:
        return None

    if authorization.startswith("Bearer "):
        token = authorization[7:]
    else:
        token = authorization

    user_token = await get_token_by_value(db, token)
    if not user_token:
        return None

    user = await get_user_by_id(db, user_token.user_id)
    return user


router = APIRouter(prefix="/api/user", tags=["users"])


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_username(db, username=user.username)

    if existing_user:
        return {
            "code": 400,
            "message": "用户名已存在",
            "data": None
        }

    new_user = await create_user(db, user=user)
    token = await create_user_token(db, new_user.id)

    return {
        "code": 200,
        "message": "注册成功",
        "data": {
            "token": token,
            "userInfo": {
                "id": new_user.id,
                "username": new_user.username,
                "bio": new_user.bio,
                "avatar": new_user.avatar
            }
        }
    }


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    verified_user = await verify_user_password(db, user.username, user.password)

    if not verified_user:
        return {
            "code": 401,
            "message": "用户名或密码错误",
            "data": None
        }

    existing_token = await get_valid_token(db, verified_user.id)

    if existing_token:
        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "token": existing_token.token,
                "userInfo": {
                    "id": verified_user.id,
                    "username": verified_user.username,
                    "nickname": None,
                    "avatar": verified_user.avatar,
                    "bio": verified_user.bio
                }
            }
        }

    new_token = await create_user_token(db, verified_user.id)

    return {
        "code": 200,
        "message": "登录成功",
        "data": {
            "token": new_token,
            "userInfo": {
                "id": verified_user.id,
                "username": verified_user.username,
                "nickname": None,
                "avatar": verified_user.avatar,
                "bio": verified_user.bio
            }
        }
    }


@router.get("/info")
async def get_user_info(current_user=Depends(get_current_user)):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }

    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": None,
            "avatar": current_user.avatar,
            "gender": "unknown",
            "bio": current_user.bio
        }
    }


@router.put("/update")
async def update_user_info(
        update_data: UserUpdate,
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }

    updated_user = await update_user(db, current_user.id, update_data)

    return {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": updated_user.id,
            "username": updated_user.username,
            "nickname": updated_user.nickname,
            "avatar": updated_user.avatar,
            "gender": updated_user.gender,
            "bio": updated_user.bio
        }
    }


@router.put("/password")
async def update_user_password(
    password_data: PasswordUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    success = await update_password(
        db,
        current_user.id,
        password_data.oldPassword,
        password_data.newPassword
    )
    
    if not success:
        return {
            "code": 400,
            "message": "原密码错误",
            "data": None
        }
    
    return {
        "code": 200,
        "message": "密码修改成功",
        "data": None
    }
