from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from schemas.favorite import FavoriteAdd
from crud.favorite import check_favorite as check_favorite_crud, add_favorite as add_favorite_crud, remove_favorite as remove_favorite_crud, get_favorite_list as get_favorite_list_crud, clear_favorites as clear_favorites_crud
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


router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
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

    is_favorite = await check_favorite_crud(db, current_user.id, newsId)

    return {
        "code": 200,
        "message": "success",
        "data": {
            "isFavorite": is_favorite
        }
    }


@router.post("/add")
async def add_favorite(
        favorite_data: FavoriteAdd,
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }

    is_favorite = await check_favorite_crud(db, current_user.id, favorite_data.newsId)

    if is_favorite:
        return {
            "code": 400,
            "message": "该新闻已收藏",
            "data": None
        }

    favorite = await add_favorite_crud(db, current_user.id, favorite_data.newsId)

    return {
        "code": 200,
        "message": "收藏成功",
        "data": {
            "id": favorite.id,
            "userId": favorite.user_id,
            "newsId": favorite.news_id,
            "createTime": favorite.created_at.isoformat() if favorite.created_at else None
        }
    }


@router.delete("/remove")
async def remove_favorite(
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
    
    is_favorite = await check_favorite_crud(db, current_user.id, newsId)
    
    if not is_favorite:
        return {
            "code": 400,
            "message": "该新闻未收藏",
            "data": None
        }
    
    success = await remove_favorite_crud(db, current_user.id, newsId)
    
    if not success:
        return {
            "code": 500,
            "message": "取消收藏失败",
            "data": None
        }
    
    return {
        "code": 200,
        "message": "取消收藏成功",
        "data": None
    }


@router.get("/list")
async def get_favorite_list(
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
    
    result = await get_favorite_list_crud(db, current_user.id, page, pageSize)
    
    return {
        "code": 200,
        "message": "success",
        "data": result
    }


@router.delete("/clear")
async def clear_favorites(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user:
        return {
            "code": 401,
            "message": "未登录或token已过期",
            "data": None
        }
    
    count = await clear_favorites_crud(db, current_user.id)
    
    message = f"成功删除{count}条收藏记录" if count > 0 else "没有收藏记录"
    
    return {
        "code": 200,
        "message": message,
        "data": None
    }
