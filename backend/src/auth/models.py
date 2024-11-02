from sqlalchemy import Column, ForeignKey, Integer, String, Text, Table
from sqlalchemy.orm import relationship
from ..database import Base
from .constant import MAX_PASSWORD_SIZE, MAX_USERNAME_SIZE

# Association table for user and news article upvotes
user_news_association_table = Table(
    "user_news_upvotes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("news_articles_id", Integer, ForeignKey("news_articles.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(MAX_USERNAME_SIZE), unique=True, nullable=False)
    hashed_password = Column(String(MAX_PASSWORD_SIZE), nullable=False)
    upvoted_news = relationship(
        "NewsArticle",
        secondary=user_news_association_table,
        back_populates="upvoted_by_users",
    )