from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base
from ..database import user_news_association_table
from ..auth.constant import MAX_PASSWORD_SIZE, MAX_USERNAME_SIZE

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