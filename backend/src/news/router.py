from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import session_opener, get_current_user
from .config import news_config
from .enums import AiModelType
from src.services.llm_client.client import OpenAIClient, AnthropicClient
from src.services.exceptions_handler import UnsupportedFeatureException, NoResourceFoundException
from src.services.logger import news_logger
from .schemas import (
    PromptRequest,
    NewsSumaryRequestSchema,
    NewsSumaryCustomModelSchema
)
from .service import (
    article_id_counter,
    fetch_news_with_details,
    toggle_upvote,
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
    keywords = openai_client.extract_search_keywords(prompt)
    news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
    for news in news_items:
        try:
            detailed_news = validate_and_parse(news).model_dump()
            detailed_news["id"] = next(article_id_counter)
            news_list.append(detailed_news)
            news_logger.search_udn_success(detailed_news["title"])
        except Exception as e:
            news_logger.search_udn_failed(news.url, error=e)
    
    if (len(news_items)):
        return sorted(news_list, key=lambda x: x["time"], reverse=True)
    else:
        raise NoResourceFoundException()

@router.post("/news_summary")
async def news_summary(
        payload: NewsSumaryRequestSchema, user=Depends(get_current_user)
):
    result = openai_client.generate_summary(payload.content)
    return result

@router.post("/{article_id}/upvote")
def upvote_article(
        article_id,
        db=Depends(session_opener),
        user=Depends(get_current_user),
):
    try:
        message = toggle_upvote(article_id, user.id, db)
        news_logger.upvote_success(article_id=article_id, user_id=user.id)
        return {"message": message}
    except Exception as e:
        news_logger.upvote_failed(article_id=article_id, user_id=user.id, error=e)
        raise

@router.post("/news_summary_custom_model")
async def news_summary_custom_model(
        payload: NewsSumaryCustomModelSchema,
        user=Depends(get_current_user)
):
    """
    Endpoint for generating a summary using either OpenAI or Anthropic.
    """
    if payload.ai_model == AiModelType.OPENAI:
        client = OpenAIClient(api_key=news_config.OPEN_AI_KEY)
    elif payload.ai_model == AiModelType.ANTHROPIC:
        client = AnthropicClient(api_key=news_config.ANTROPIC_AI_KEY)
    else:
        raise UnsupportedFeatureException(feature_name=f"model type: {payload.ai_model}")

    result = client.generate_summary(payload.content)
    return result