from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from models.news import Category, News

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Category).order_by(Category.sort_order).offset(skip).limit(limit)
    )
    categories = result.scalars().all()
    
    serialized_categories = []
    for category in categories:
        serialized_categories.append({
            "id": category.id,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
            "name": category.name,
            "sort_order": category.sort_order
        })
    
    return serialized_categories

async def get_news_list(db: AsyncSession, category_id: int = None, page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    
    query = select(News).options(selectinload(News.category)).order_by(News.publish_time.desc())
    
    if category_id is not None:
        query = query.filter(News.category_id == category_id)
    
    total_query = select(func.count(News.id))
    if category_id is not None:
        total_query = total_query.filter(News.category_id == category_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    result = await db.execute(query.offset(skip).limit(page_size))
    news_list = result.scalars().all()
    
    has_more = (skip + page_size) < total
    
    serialized_list = []
    for news in news_list:
        news_dict = {
            "id": news.id,
            "publish_time": news.publish_time,
            "created_at": news.created_at,
            "updated_at": news.updated_at,
            "category_id": news.category_id,
            "title": news.title,
            "description": news.description,
            "content": news.content,
            "image": news.image,
            "author": news.author,
            "views": news.views,
            "category": None
        }
        if news.category:
            news_dict["category"] = {
                "id": news.category.id,
                "created_at": news.category.created_at,
                "updated_at": news.category.updated_at,
                "name": news.category.name,
                "sort_order": news.category.sort_order
            }
        serialized_list.append(news_dict)
    
    return {
        "list": serialized_list,
        "total": total,
        "hasMore": has_more
    }

async def get_news_detail(db: AsyncSession, news_id: int):
    result = await db.execute(
        select(News).options(selectinload(News.category)).where(News.id == news_id)
    )
    news = result.scalar_one_or_none()
    
    if not news:
        return None
    
    news.views += 1
    await db.commit()
    await db.refresh(news)
    
    news_dict = {
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views,
        "relatedNews": []
    }
    
    related_result = await db.execute(
        select(News)
        .where(News.category_id == news.category_id, News.id != news_id)
        .order_by(News.publish_time.desc())
        .limit(5)
    )
    related_news = related_result.scalars().all()
    
    serialized_related = []
    for item in related_news:
        serialized_related.append({
            "id": item.id,
            "publish_time": item.publish_time,
            "title": item.title,
            "description": item.description,
            "image": item.image,
            "views": item.views
        })
    
    news_dict["relatedNews"] = serialized_related
    
    return news_dict
