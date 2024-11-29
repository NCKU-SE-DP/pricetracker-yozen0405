from bs4 import BeautifulSoup
import requests
import json

from ..database import SessionLocal
from src.services.crawler.udn_crawler import UDNCrawler
from src.services.llm_client.openai_client import OpenAIClient
from .config import news_config

crawler = UDNCrawler()
openai_client = OpenAIClient()

def convert_news_to_dict(news):
    return {
        "url": news.url,
        "title": news.title,
        "time": news.time,
        "content": news.content,
    }

def process_news_item(news):
    """
    Fetches detailed content from a news article.
    """
    return crawler.parse(news.url)

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
    
def add_news_summary(news, summary_result):
    return crawler.add_news_summary(news=news, summary_result=summary_result)

def parse_summary_result(result):
    """
    Parses the summary result JSON and extracts 'summary' and 'reason'.

    :param result: The JSON-formatted summary result string.
    :return: A dictionary with keys 'summary' and 'reason', or an empty dictionary if parsing fails.
    """
    response_data = {}
    if result:
        try:
            result = json.loads(result)
            response_data["summary"] = result["影響"]
            response_data["reason"] = result["原因"]
        except json.JSONDecodeError:
            return response_data
    return response_data