from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    sort_order: int

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int
    views: int = 0

class NewsCreate(NewsBase):
    pass

class News(NewsBase):
    id: int
    publish_time: datetime
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True

class NewsListResponse(BaseModel):
    list: list[News]
    total: int
    hasMore: bool
