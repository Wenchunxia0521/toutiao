from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from models.favorite import Favorite
from models.news import News
from datetime import datetime

async def check_favorite(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id
        )
    )
    return result.scalar_one_or_none() is not None

async def add_favorite(db: AsyncSession, user_id: int, news_id: int):
    favorite = Favorite(
        user_id=user_id,
        news_id=news_id,
        created_at=datetime.utcnow()
    )
    db.add(favorite)
    await db.flush()
    await db.refresh(favorite)
    return favorite

async def remove_favorite(db: AsyncSession, user_id: int, news_id: int):
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        return False
    
    await db.execute(
        delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.news_id == news_id
        )
    )
    await db.flush()
    return True

async def get_favorite_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    
    # 查询总数
    total_query = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 查询收藏记录
    query = (
        select(Favorite, News)
        .join(News, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .offset(skip)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    list = []
    for favorite, news in rows:
        list.append({
            "id": news.id,
            "title": news.title,
            "description": news.description or "",
            "image": news.image or "",
            "author": news.author or "",
            "publishTime": news.publish_time.isoformat() if news.publish_time else None,
            "categoryId": news.category_id,
            "views": news.views,
            "favoriteTime": favorite.created_at.isoformat() if favorite.created_at else None
        })
    
    has_more = (skip + page_size) < total
    
    return {
        "list": list,
        "total": total,
        "hasMore": has_more
    }

async def clear_favorites(db: AsyncSession, user_id: int):
    # 先查询有多少条收藏
    count_query = select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    count = count_result.scalar() or 0
    
    # 删除所有收藏
    if count > 0:
        await db.execute(
            delete(Favorite).where(Favorite.user_id == user_id)
        )
        await db.flush()
    
    return count