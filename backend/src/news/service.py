import itertools
from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete

from .models import NewsArticle
from ..users.models import user_news_association_table
from ..ai_service.service import relevance_check, generate_summary
from .utils import (
    process_news_item,
    fetch_news_articles_by_keyword, 
    add_news_article,
    add_news_summary
)

# Unique ID counter for generating temporary article IDs in memory.
article_id_counter = itertools.count(start=1000000)

def fetch_and_process_news(is_initial=False):
    """
    Fetches news articles and processes them to assess relevance and generate summaries.

    :param is_initial: If True, fetches multiple pages of news articles.
    :return: None
    """
    news_articles = fetch_news_articles_by_keyword("價格", is_initial=is_initial)

    # Iterate through each news article
    for article in news_articles:
        article_title = article.title
        relevance = relevance_check(article_title)
        if relevance == "high":
            detailed_news = process_news_item(article)
            summary_result = generate_summary(detailed_news.content)
            detailed_news = add_news_summary(detailed_news, summary_result)
            add_news_article(detailed_news)

def get_article_upvote_details(article_id, uid, db):
    """
    Retrieves upvote count and user-specific upvote status for an article.
    
    :param article_id: The ID of the news article.
    :param uid: User ID (or None for anonymous).
    :param db: Database session for querying.
    :return: Tuple containing upvote count and user-specific upvote status.
    """
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

