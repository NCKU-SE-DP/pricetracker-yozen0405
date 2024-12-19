from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ..dependencies import session_opener, get_current_user
from .config import news_config
from .models import NewsArticle
from .enums import AiModelType
from src.services.llm_client.client import OpenAIClient, AnthropicClient
from .schemas import (
    PromptRequest,
    NewsSumaryRequestSchema,
    NewsSumaryCustomModelSchema
)
from .service import (
    article_id_counter,
    get_article_upvote_details,
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
    news = db.query(NewsArticle).order_by(NewsArticle.time.desc()).all()
    result = []
    for article in news:
        upvotes, upvoted = get_article_upvote_details(article.id, None, db)
        result.append(
            {**article.__dict__, "upvotes": upvotes, "is_upvoted": upvoted}
        )
    return result

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

@router.post("/search_news")
async def search_news_articles(request: PromptRequest):
    prompt = request.prompt
    news_list = []
    keywords = openai_client.extract_search_keywords(prompt)
    news_items = fetch_news_articles_by_keyword(keywords, is_initial=False)
    for news in news_items:
        try:
            detailed_news = validate_and_parse(news).model_dump()
            detailed_news["id"] = next(article_id_counter)
            news_list.append(detailed_news)
        except Exception as e:
            print(e)
    return sorted(news_list, key=lambda x: x["time"], reverse=True)

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
    message = toggle_upvote(article_id, user.id, db)
    return {"message": message}

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
        raise HTTPException(status_code=400, detail=f"Unsupported model type: {payload.ai_model}")

    try:
        result = client.generate_summary(payload.content)
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")