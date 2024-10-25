import itertools
import requests
from urllib.parse import quote
import json
from bs4 import BeautifulSoup
from openai import OpenAI

from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete

from ..database import Session
from .models import NewsArticle
from ..auth.models import user_news_association_table
from .config import news_config

_id_counter = itertools.count(start=1000000)

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
            response = requests.get(news_config.UDN_API_URL, params=request_params)
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
