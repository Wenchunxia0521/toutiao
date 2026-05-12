from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0)

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    publish_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("categories.id"))
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    content = Column(String)
    image = Column(String(255))
    author = Column(String(100))
    views = Column(Integer, default=0)
    
    category = relationship("Category")
