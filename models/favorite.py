from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Favorite(Base):
    __tablename__ = "favorite"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    news_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)