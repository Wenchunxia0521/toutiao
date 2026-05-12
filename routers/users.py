from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.users import UserCreate
from crud.users import get_user_by_username, create_user, create_user_token
from config.db_conf import get_db

router=APIRouter(prefix="/api/user",tags=["users"])

@router.post("/register")
async def register(user:UserCreate,db:AsyncSession=Depends(get_db)):
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