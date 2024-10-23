import json
import sentry_sdk
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi.middleware.cors import CORSMiddleware
import itertools
from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session, sessionmaker
from typing import List, Optional
import requests
from fastapi import APIRouter, HTTPException, Query, Depends, status, FastAPI
import os
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from pydantic import BaseModel, Field, AnyHttpUrl
from sqlalchemy import (Column, ForeignKey, Integer, String, Table, Text,
                        create_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


user_news_association_table = Table(
    "user_news_upvotes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column(
        "news_articles_id", Integer, ForeignKey("news_articles.id"), primary_key=True
    ),
)

# from pydantic import BaseModel

MaxUsernameSize = 50 
MaxPasswordSize = 200
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(MaxUsernameSize), unique=True, nullable=False)
    hashed_password = Column(String(MaxPasswordSize), nullable=False)
    upvoted_news = relationship(
        "NewsArticle",
        secondary=user_news_association_table,
        back_populates="upvoted_by_users",
    )

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)  
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    time = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    upvoted_by_users = relationship(
        "User", secondary=user_news_association_table, back_populates="upvoted_news"
    )

engine = create_engine("sqlite:///news_database.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

sentry_sdk.init(
    dsn="https://4001ffe917ccb261aa0e0c34026dc343@o4505702629834752.ingest.us.sentry.io/4507694792704000",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app = FastAPI()
schedulers = BackgroundScheduler()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from openai import OpenAI

# def generate_summary(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content

#
# def extract_search_keywords(content):
#     m = [
#         {
#             "role": "system",
#             "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
#         },
#         {"role": "user", "content": f"{content}"},
#     ]
#
#     completion = OpenAI(api_key="xxx").chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=m,
#     )
#     return completion.choices[0].message.content

from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

def add_news_article(news_article_data):
    """
    add new to db
    :param news_data: news info
    :return:
    """
    session = Session()
    session.add(NewsArticle(
        url=news_article_data["url"],
        title=news_article_data["title"],
        time=news_article_data["time"],
        content=" ".join(news_article_data["content"]),  # 將內容list轉換為字串
        summary=news_article_data["summary"],
        reason=news_article_data["reason"],
    ))
    session.commit()
    session.close()

def fetch_news_articles_by_keyword(search_term, is_initial=False):
    """
    Fetches news articles based on the search keyword.

    :param search_term: The search keyword.
    :param is_initial: Boolean flag indicating whether this is the initial fetch.
    :return: List of news articles.
    """
    all_news_data = []
    
    # Iterate pages to get more news data
    if is_initial:
        for page in range(1, 10):
            request_params = {
                "page": page,
                "id": f"search:{quote(search_term)}",
                "channelId": 2,
                "type": "searchword",
            }
            response = requests.get("https://udn.com/api/more", params=request_params)
            all_news_data.extend(response.json()["lists"])  # Append each page's news data without re-adding

    else:
        request_params = {
            "page": 1,
            "id": f"search:{quote(search_term)}",
            "channelId": 2,
            "type": "searchword",
        }
        response = requests.get("https://udn.com/api/more", params=request_params)
        all_news_data = response.json()["lists"]

    return all_news_data


def fetch_and_process_news(is_initial=False):
    """
    get new info

    :param is_initial:
    :return:
    """
    news_articles = fetch_news_articles_by_keyword("價格", is_initial=is_initial)

    # Iterate through each news article
    for article in news_articles:
        article_title = article["title"]
        relevance_check_prompt = [
            {
                "role": "system",
                "content": "你是一個關聯度評估機器人，請評估新聞標題是否與「民生用品的價格變化」相關，並給予'high'、'medium'、'low'評價。(僅需回答'high'、'medium'、'low'三個詞之一)",
            },
            {"role": "user", "content": f"{article_title}"},
        ]
        ai_response = OpenAI(api_key="xxx").chat.completions.create(
            model="gpt-3.5-turbo",
            messages=relevance_check_prompt,
        )
        relevance = ai_response.choices[0].message.content
        if relevance == "high":
            response = requests.get(article["titleLink"])
            soup = BeautifulSoup(response.text, "html.parser")
            # 標題
            detailed_title = soup.find("h1", class_="article-content__title").text
            publication_time = soup.find("time", class_="article-content__time").text
            # 定位到包含文章内容的 <section>
            content_section = soup.find("section", class_="article-content__editor")

            content_paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            detailed_news =  {
                "url": article["titleLink"],
                "title": detailed_title,
                "time": publication_time,
                "content": content_paragraphs,
            }
            summary_prompt = [
                {
                    "role": "system",
                    "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
                },
                {"role": "user", "content": " ".join(detailed_news["content"])},
            ]

            summary_completion = OpenAI(api_key="xxx").chat.completions.create(
                model="gpt-3.5-turbo",
                messages=summary_prompt,
            )
            summary_result = summary_completion.choices[0].message.content
            summary_result = json.loads(summary_result)
            detailed_news["summary"] = summary_result["影響"]
            detailed_news["reason"] = summary_result["原因"]
            add_news_article(detailed_news)

@app.on_event("startup")
def start_scheduler():
    db = SessionLocal()
    if db.query(NewsArticle).count() == 0:
        # should change into simple factory pattern
        fetch_and_process_news()
    db.close()
    schedulers.add_job(fetch_and_process_news, "interval", minutes=100)
    schedulers.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    schedulers.shutdown()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

def session_opener():
    session = Session(bind=engine)
    try:
        yield session
    finally:
        session.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def validate_user_credentials(db_session, username, password):
    user = db_session.query(User).filter(User.username == username).first()
    if not verify_password(password, user.hashed_password):
        return False
    return user

def authenticate_user_token(
    token = Depends(oauth2_scheme),
    db = Depends(session_opener)
):
    payload = jwt.decode(token, '1892dhianiandowqd0n', algorithms=["HS256"])
    return db.query(User).filter(User.username == payload.get("sub")).first()

def create_access_token(user_data, expires_delta=None):
    """create access token"""
    to_encode = user_data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    print(to_encode)
    encoded_jwt = jwt.encode(to_encode, '1892dhianiandowqd0n', algorithm="HS256")
    return encoded_jwt

@app.post("/api/v1/users/login")
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(session_opener)
):
    """login"""
    user = validate_user_credentials(db, form_data.username, form_data.password)
    access_token = create_access_token(
        user_data={"sub": str(user.username)}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

class UserAuthSchema(BaseModel):
    username: str
    password: str

@app.post("/api/v1/users/register")
def create_user(user: UserAuthSchema, db: Session = Depends(session_opener)):
    """create user"""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/v1/users/me")
def read_users_me(user=Depends(authenticate_user_token)):
    return {"username": user.username}

_id_counter = itertools.count(start=1000000)

def get_article_upvote_details(article_id, uid, db):
    upvote_count = (
        db.query(user_news_association_table)
        .filter_by(news_articles_id=article_id)
        .count()
    )

    has_voted = False
    if uid:
        has_voted = (
            db.query(user_news_association_table)
            .filter_by(news_articles_id=article_id, user_id=uid)
            .first() is not None
        )

    return upvote_count, has_voted

@app.get("/api/v1/news/news")
def fetch_news_with_upvote_details(db=Depends(session_opener)):
    """
    read new

    :param db:
    :return:
    """
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, None, db)
        result.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
        )
    return result

@app.get(
    "/api/v1/news/user_news"
)
def get_user_specific_news(
        db=Depends(session_opener),
        user=Depends(authenticate_user_token)
):
    """
    read user new

    :param db:
    :param user:
    :return:
    """
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, user.id, db)
        result.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )
    return result

class PromptRequest(BaseModel):
    prompt: str

@app.post("/api/v1/news/search_news")
async def search_news_articles(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    keyword_extraction_prompt = [
        {
            "role": "system",
            "content": "你是一個關鍵字提取機器人，用戶將會輸入一段文字，表示其希望看見的新聞內容，請提取出用戶希望看見的關鍵字，請截取最重要的關鍵字即可，避免出現「新聞」、「資訊」等混淆搜尋引擎的字詞。(僅須回答關鍵字，若有多個關鍵字，請以空格分隔)",
        },
        {"role": "user", "content": f"{prompt}"},
    ]

    completion = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=keyword_extraction_prompt,
    )
    keywords = completion.choices[0].message.content
    # should change into simple factory pattern
    news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
    for news in news_items:
        try:
            response = requests.get(news["titleLink"])
            soup = BeautifulSoup(response.text, "html.parser")
            # 標題
            title = soup.find("h1", class_="article-content__title").text
            time = soup.find("time", class_="article-content__time").text
            # 定位到包含文章内容的 <section>
            content_section = soup.find("section", class_="article-content__editor")

            paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            detailed_news = {
                "url": news["titleLink"],
                "title": title,
                "time": time,
                "content": paragraphs,
            }
            detailed_news["content"] = " ".join(detailed_news["content"])
            detailed_news["id"] = next(_id_counter)
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)

class NewsSumaryRequestSchema(BaseModel):
    content: str

@app.post("/api/v1/news/news_summary")
async def news_summary(
        payload: NewsSumaryRequestSchema, user=Depends(authenticate_user_token)
):
    response_data = {}
    summary_generation_prompt = [
        {
            "role": "system",
            "content": "你是一個新聞摘要生成機器人，請統整新聞中提及的影響及主要原因 (影響、原因各50個字，請以json格式回答 {'影響': '...', '原因': '...'})",
        },
        {"role": "user", "content": f"{payload.content}"},
    ]

    completion = OpenAI(api_key="xxx").chat.completions.create(
        model="gpt-3.5-turbo",
        messages=summary_generation_prompt,
    )
    result = completion.choices[0].message.content
    if result:
        result = json.loads(result)
        response_data["summary"] = result["影響"]
        response_data["reason"] = result["原因"]
    return response_data


@app.post("/api/v1/news/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        user=Depends(authenticate_user_token),
):
    message = toggle_upvote(article_id, user.id, db)
    return {"message": message}

def toggle_upvote(article_id, uid, db_session):
    """
    Toggles the upvote status for a specific article by a user.

    :param article_id: The ID of the news article.
    :param user_id: The ID of the user.
    :param db_session: The database session for executing queries.
    :return: A message indicating whether the upvote was added or removed.
    """
    # Check if the user has already upvoted the article
    existing_upvote = db_session.execute(
        select(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == article_id,
            user_news_association_table.c.user_id == uid,
        )
    ).scalar()

    # If upvote exists, remove it
    if existing_upvote:
        delete_stmt = delete(user_news_association_table).where(
            user_news_association_table.c.news_articles_id == article_id,
            user_news_association_table.c.user_id == uid,
        )
        db_session.execute(delete_stmt)
        db_session.commit()
        return "Upvote removed"

    # Otherwise, add a new upvote
    else:
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=article_id, user_id=uid
        )
        db_session.execute(insert_stmt)
        db_session.commit()
        return "Article upvoted"


def news_exists(article_id, db: Session):
    return db.query(NewsArticle).filter_by(id=article_id).first() is not None


@app.get("/api/v1/prices/necessities-price")
def get_necessities_prices(
        category=Query(None), commodity=Query(None)
):
    return requests.get(
        "https://opendata.ey.gov.tw/api/ConsumerProtection/NecessitiesPrice",
        params={"CategoryName": category, "Name": commodity},
    ).json()