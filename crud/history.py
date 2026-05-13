from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.history import History
from models.news import News
from datetime import datetime

async def add_history(db: AsyncSession, user_id: int, news_id: int):
    history = History(
        user_id=user_id,
        news_id=news_id,
        view_time=datetime.utcnow()
    )
    db.add(history)
    await db.flush()
    await db.refresh(history)
    return history

async def get_history_list(db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    
    # 查询总数
    total_query = select(func.count(History.id)).where(History.user_id == user_id)
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # 查询浏览记录
    query = (
        select(History, News)
        .join(News, History.news_id == News.id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset(skip)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    list = []
    for history, news in rows:
        list.append({
            "id": news.id,
            "title": news.title,
            "description": news.description or "",
            "image": news.image or "",
            "author": news.author or "",
            "publishTime": news.publish_time.isoformat() if news.publish_time else None,
            "categoryId": news.category_id,
            "views": news.views,
            "viewTime": history.view_time.isoformat() if history.view_time else None
        })
    
    has_more = (skip + page_size) < total
    
    return {
        "list": list,
        "total": total,
        "hasMore": has_more
    }

async def delete_history(db: AsyncSession, user_id: int, news_id: int):
    stmt = delete(History).where(
        History.user_id == user_id,
        History.news_id == news_id
    )
    result = await db.execute(stmt)
    await db.flush()
    return result.rowcount > 0

async def clear_history(db: AsyncSession, user_id: int):
    stmt = delete(History).where(History.user_id == user_id)
    await db.execute(stmt)
    await db.flush()