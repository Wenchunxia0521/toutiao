from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from schemas.history import HistoryAdd
from crud.history import add_history as add_history_crud, get_history_list as get_history_list_crud, delete_history as delete_history_crud, clear_history as clear_history_crud
from crud.users import get_token_by_value, get_user_by_id
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

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    history_data: HistoryAdd,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    history = await add_history_crud(db, current_user.id, history_data.newsId)
    
    return {
        "code": 200,
        "message": "添加成功",
        "data": {
            "id": history.id,
            "userId": history.user_id,
            "newsId": history.news_id,
            "viewTime": history.view_time.isoformat() if history.view_time else None
        }
    }


@router.get("/list")
async def get_history_list(
    page: int = Query(1),
    pageSize: int = Query(10, le=100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    result = await get_history_list_crud(db, current_user.id, page, pageSize)
    
    return {
        "code": 200,
        "message": "success",
        "data": result
    }


@router.delete("/delete/{newsId}")
async def delete_history(
    newsId: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    success = await delete_history_crud(db, current_user.id, newsId)
    
    if success:
        return {
            "code": 200,
            "message": "删除成功",
            "data": None
        }
    else:
        return {
            "code": 404,
            "message": "浏览记录不存在",
            "data": None
        }


@router.delete("/clear")
async def clear_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    await clear_history_crud(db, current_user.id)
    
    return {
        "code": 200,
        "message": "清空成功",
        "data": None
    }