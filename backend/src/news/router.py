from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..dependencies import session_opener, get_current_user
from src.services.logger import news_logger
from src.services.llm_client.exceptions import LLMClientExceptionBase
from src.services.crawler.exceptions import CrawlerExceptionsBase
from .schemas import (
    PromptRequest,
    NewsSumaryRequestSchema,
    NewsSumaryCustomModelSchema
)
from .service import (
    article_id_counter,
    fetch_news_with_details,
    toggle_upvote,
    generate_summary
)
from .utils import (
    fetch_news_articles_by_keyword,
    validate_and_parse,
    openai_client
)

router = APIRouter(
    prefix="/news",
    tags=["News"],
    responses={404: {"description": "Not found"}},
)

@router.get("/news")
def fetch_news_with_upvote_details(db: Session = Depends(session_opener)):
    """
    Fetch all news articles with their upvote details.

    :param db: Database session dependency for querying news articles.
    :return: A list of news articles with upvote count and upvoted status.
    """
    return fetch_news_with_details(db)

@router.get("/user_news")
def get_user_specific_news(
    db: Session = Depends(session_opener),
    user = Depends(get_current_user)
):
    """
    Fetch news articles specific to the authenticated user.

    :param db: Database session dependency for querying news articles.
    :param user: Authenticated user dependency for user-specific data.
    :return: A list of news articles with upvote count and the user's upvoted status.
    """
    return fetch_news_with_details(db, user_id=user.id)

@router.post("/search_news")
async def search_news_articles(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    news_logger.searching_udn_news()

    try:
        keywords = openai_client.extract_search_keywords(prompt)
    except LLMClientExceptionBase as e:
        raise HTTPException(status_code=500, detail="Unexcepted error happened, please try later")

    try:
        news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
    except CrawlerExceptionsBase as e:
        raise HTTPException(status_code=500, detail="Unexcepted error happened, please try later")

    for news in news_items:
        try:
            detailed_news = validate_and_parse(news).model_dump()
        except CrawlerExceptionsBase as e:
            news_logger.search_udn_failed(news.url, error=e)
            continue

        detailed_news["id"] = next(article_id_counter)
        news_list.append(detailed_news)
        news_logger.search_udn_success(detailed_news["title"])
    
    return sorted(news_list, key=lambda x: x["time"], reverse=True)

@router.post("/news_summary")
async def news_summary(
        payload: NewsSumaryRequestSchema, user=Depends(get_current_user)
):
    return generate_summary(payload.content)

@router.post("/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        user=Depends(get_current_user),
):
    message = toggle_upvote(article_id, user.id, db)
    return {"message": message}

@router.post("/news_summary_custom_model")
async def news_summary_custom_model(
        payload: NewsSumaryCustomModelSchema,
        user=Depends(get_current_user)
):
    return generate_summary(payload.content, payload.ai_model)