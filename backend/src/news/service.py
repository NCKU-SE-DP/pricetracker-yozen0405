import itertools
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, insert, delete
from typing import Optional
from sentry_sdk import capture_exception

from src.services.llm_client.client import OpenAIClient, AnthropicClient
from .config import news_config
from .enums import AiModelType
from .models import NewsArticle
from src.services.llm_client.enum import RelevanceLevel
from src.services.llm_client.exceptions import InvalidResponseFormatException, LLMRequestFailedException, LLMClientExceptionBase
from src.services.crawler.exceptions import CrawlerExceptionsBase
from src.services.logger import news_logger
from ..users.models import user_news_association_table
from .exceptions import NewsDoesntExistException
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
        except LLMRequestFailedException as e:
            news_logger.error_processing_article(title=article_title, error=e)
            continue

        if relevance == RelevanceLevel.HIGH:
            try:
                detailed_news = validate_and_parse(article)
            except CrawlerExceptionsBase as e:
                continue
            
            try:
                summary_result = openai_client.generate_summary(detailed_news.content)
            except LLMClientExceptionBase as e:
                continue

            detailed_news = add_news_summary(detailed_news, summary_result)
            try:
                add_news_article(detailed_news)
            except CrawlerExceptionsBase as e:
                continue

            news_logger.added_high_relevance_article(title=article_title)

def get_article_upvote_details(article_id, uid, db):
    """
    Retrieves upvote count and user-specific upvote status for an article.
    
    :param article_id: The ID of the news article.
    :param uid: User ID (or None for anonymous).
    :param db: Database session for querying.
    :return: Tuple containing upvote count and user-specific upvote status.
    """
    if not news_exists(article_id, db):
        news_logger.error_processing_article(article_id=article_id, user_id=uid)
        raise NewsDoesntExistException()
    
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
        capture_exception(e)
        raise HTTPException(status_code=500, detail="Unexcepted error occured.")

    result = []
    for article in news:
        try:
            upvotes, upvoted = get_article_upvote_details(article.id, user_id, db)
        except NewsDoesntExistException as e:
            capture_exception(e)
            news_logger.fetch_db_news_failed(e)
            continue

        result.append(
            {
                **article.__dict__,
                "upvotes": upvotes,
                "is_upvoted": upvoted,
            }
        )

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
    if not news_exists(article_id, db_session):
        raise NewsDoesntExistException()
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

        try:
            db_session.commit()
        except SQLAlchemyError as e:
            news_logger.toggle_article_failed(article_id=article_id, user_id=uid, error=e)
            capture_exception(e)
            raise HTTPException(status_code=500, detail="Unexcepted error happened, please tried again")
        
        news_logger.upvote_removed(article_id=article_id, user_id=uid)
        return "Upvote removed"
    # Otherwise, add a new upvote
    else:
        insert_stmt = insert(user_news_association_table).values(
            news_articles_id=article_id, user_id=uid
        )
        db_session.execute(insert_stmt)

        try:
            db_session.commit()
        except SQLAlchemyError as e:
            news_logger.toggle_article_failed(article_id=article_id, user_id=uid, error=e)
            capture_exception(e)
            raise HTTPException(status_code=500, detail="Unexcepted error happened, please tried again")
        
        news_logger.upvote_added(article_id=article_id, user_id=uid)
        return "Article upvoted"

def news_exists(article_id, db: Session):
    try:
        exists = db.query(NewsArticle).filter_by(id=article_id).first()
    except SQLAlchemyError as e:
        news_logger.fetch_db_news_failed(error=e)
        capture_exception(e)
        raise

    if not exists:
        news_logger.article_not_found(article_id=article_id)
        return exists

def generate_summary(content: str, ai_model: str = AiModelType.OPENAI.value):
    if ai_model == AiModelType.OPENAI.value:
        client = OpenAIClient(api_key=news_config.OPEN_AI_KEY)
    elif ai_model == AiModelType.ANTHROPIC.value:
        client = AnthropicClient(api_key=news_config.ANTROPIC_AI_KEY)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid AI model type, should be one of the {AiModelType.OPENAI.value} or {AiModelType.ANTHROPIC.value}.")

    try:
        return client.generate_summary(content)
    except InvalidResponseFormatException as e:
        raise HTTPException(status_code=400, detail="Please provide a different or longer content")
    except LLMRequestFailedException as e:
        raise HTTPException(status_code=500, detail="Unexcepted error happened, our client service is down, please tried again after a while.")
    except Exception as e:
        capture_exception(e)
        raise HTTPException(status_code=500, detail="Unexcepted error happened, failed to generate summary")