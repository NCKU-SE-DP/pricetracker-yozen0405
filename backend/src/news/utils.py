import json

from ..database import SessionLocal
from src.services.crawler.udn_crawler import UDNCrawler
from src.services.llm_client.client import OpenAIClient
from src.news.config import news_config
from src.services.crawler.crawler_base import NewsWithSummary

crawler = UDNCrawler()
openai_client = OpenAIClient(api_key=news_config.OPEN_AI_KEY)

def validate_and_parse(news):
    """
    Fetches detailed content from a news article.
    """
    return crawler.validate_and_parse(news.url)

def add_news_article(news_article_data):
    """
    Adds a news article to the database.

    :param news_article_data: Dictionary containing article information.
    :return: None
    """
    session = SessionLocal()
    crawler.save(news=news_article_data, db=session)

def fetch_news_articles_by_keyword(search_term, is_initial=False):
    """
    Fetches news articles from UDN based on the provided search keyword.
    
    :param search_term: The keyword to search for in news articles.
    :param is_initial: If True, fetches multiple pages of news; otherwise, fetches only the first page.
    :return: List of news articles.
    """
    if is_initial:
        return crawler.startup(search_term=search_term)
    else:
        return crawler.get_headline(search_term=search_term, page=1)
    
def add_news_summary(news, summary_data):
    summary = summary_data["影響"]
    reason = summary_data["原因"]
    news_with_summary = NewsWithSummary(
        title=news.title,
        url=news.url,
        time=news.time,
        content=news.content,
        summary=summary,
        reason=reason,
    )
    return news_with_summary
