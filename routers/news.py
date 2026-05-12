from fastapi import APIRouter,Query,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_conf import  get_db
from crud.news import get_categories as get_categories_crud, get_news_list as get_news_list_crud, get_news_detail as get_news_detail_crud
from schemas.news import Category

router=APIRouter(prefix="/api/news",tags=["news"])

@router.get("/categories")
async def get_categories(skip:int=Query(0),limit:int=Query(10),db:AsyncSession=Depends(get_db)):
    categories = await get_categories_crud(db, skip=skip, limit=limit)
    return {
        "code": 200,
        "message": "success",
        "data": categories
    }

@router.get("/list")
async def get_news_list(categoryId:int=Query(None),page:int=Query(1),pageSize:int=Query(10),db:AsyncSession=Depends(get_db)):
    news_data = await get_news_list_crud(db, category_id=categoryId, page=page, page_size=pageSize)
    return {
        "code": 200,
        "message": "success",
        "data": news_data
    }

@router.get("/detail")
async def get_news_detail(id:int,db:AsyncSession=Depends(get_db)):
    news_detail = await get_news_detail_crud(db, news_id=id)
    
    if not news_detail:
        return {
            "code": 404,
            "message": "新闻不存在",
            "data": None
        }
    
    return {
        "code": 200,
        "message": "success",
        "data": news_detail
    }