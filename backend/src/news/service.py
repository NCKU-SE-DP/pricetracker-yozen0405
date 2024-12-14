import itertools
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, insert, delete
from typing import Optional

from .models import NewsArticle
from src.services.llm_client.enum import RelevanceLevel
from src.services.exceptions_handler import ArticleNotFoundException, InternalServerErrorException
from src.services.logger import news_logger
from ..users.models import user_news_association_table
from .utils import (
    validate_and_parse,
    fetch_news_articles_by_keyword, 
    add_news_article,
    add_news_summary,
    openai_client
)

# Unique ID counter for generating temporary article IDs in memory.
article_id_counter = itertools.count(start=1000000)

def fetch_and_process_news(is_initial=False):
    """
    Fetches news articles and processes them to assess relevance and generate summaries.

    :param is_initial: If True, fetches multiple pages of news articles.
    :return: None
    """
    try:
        news_articles = fetch_news_articles_by_keyword("價格", is_initial=is_initial)
    except Exception as e:
        raise

    for article in news_articles:
        article_title = article.title
        try:
            relevance = openai_client.evaluate_relevance(article_title)

            if relevance == RelevanceLevel.HIGH:
                detailed_news = validate_and_parse(article)
                summary_result = openai_client.generate_summary(detailed_news.content)
                detailed_news = add_news_summary(detailed_news, summary_result)
                add_news_article(detailed_news)
                news_logger.added_high_relevance_article(title=article_title)

        except Exception as e:
            news_logger.error_processing_article(title=article_title, error=e)

def get_article_upvote_details(article_id, uid, db):
    """
    Retrieves upvote count and user-specific upvote status for an article.
    
    :param article_id: The ID of the news article.
    :param uid: User ID (or None for anonymous).
    :param db: Database session for querying.
    :return: Tuple containing upvote count and user-specific upvote status.
    """
    try:
        if not news_exists(article_id, db):
            news_logger.error_processing_article(article_id=article_id, user_id=uid)
            raise InternalServerErrorException()
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
        news_logger.get_upvote_count_success(article_id=article_id, user_id=uid, upvote_count=upvote_count, has_voted=has_voted)

        return upvote_count, has_voted
    except SQLAlchemyError as e:
        news_logger.get_upvote_count_failed(article_id=article_id, user_id=uid, error=e)
        raise
    
def fetch_news_with_details(db: Session, user_id: Optional[int] = None) -> list:
    """
    Fetch all news articles with their upvote details.

    :param db: Database session dependency for querying news articles.
    :param user_id: Optional user ID to fetch user-specific upvote status.
    :return: A list of news articles with upvote count and user-specific upvote status.
    """
    try:
        news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    except SQLAlchemyError as e:
        news_logger.fetch_db_news_failed(e)
        raise InternalServerErrorException(e)

    result = []
    for article in news:
        try:
            upvotes, upvoted = get_article_upvote_details(article.id, user_id, db)
            result.append(
                {
                    **article.__dict__,
                    "upvotes": upvotes,
                    "is_upvoted": upvoted,
                }
            )
        except Exception as e:
            news_logger.fetch_db_news_failed(e)

    news_logger.fetch_db_news_success(len(result))
    return result

def toggle_upvote(article_id, uid, db_session):
    """
    Toggles the upvote status for a specific article by a user.

    :param article_id: The ID of the news article.
    :param user_id: The ID of the user.
    :param db_session: The database session for executing queries.
    :return: A message indicating whether the upvote was added or removed.
    """
    try:
        if not news_exists(article_id, db_session):
            raise ArticleNotFoundException()

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
            news_logger.upvote_removed(article_id=article_id, user_id=uid)
            return "Upvote removed"

        # Otherwise, add a new upvote
        else:
            insert_stmt = insert(user_news_association_table).values(
                news_articles_id=article_id, user_id=uid
            )
            db_session.execute(insert_stmt)
            db_session.commit()
            news_logger.upvote_added(article_id=article_id, user_id=uid)
            return "Article upvoted"
        
    except SQLAlchemyError as e:
        news_logger.toggle_article_failed(article_id=article_id, user_id=uid, error=e)
        raise InternalServerErrorException(e)

def news_exists(article_id, db: Session):
    try:
        exists = db.query(NewsArticle).filter_by(id=article_id).first()
        if not exists:
            news_logger.article_not_found(article_id=article_id)
        return exists
    except SQLAlchemyError as e:
        news_logger.fetch_db_news_failed(error=e)
        raise

