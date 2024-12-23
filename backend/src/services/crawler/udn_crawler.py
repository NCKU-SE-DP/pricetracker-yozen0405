"""
UDN News Scraper Module

This module provides the UDNCrawler class for fetching, parsing, and saving news articles from the UDN website.
The class extends the NewsCrawlerBase and includes functionalities to search for news articles based on a search term,
parse the details of individual articles, and save them to a database using SQLAlchemy ORM.

Classes:
    UDNCrawler: A class to scrape news from UDN.

Exceptions:
    DomainMismatchException: Raised when the URL domain does not match the expected domain for the crawler.

Usage Example:
    crawler = UDNCrawler(timeout=10)
    headlines = crawler.startup("technology")
    for headline in headlines:
        news = crawler.parse(headline.url)
        crawler.save(news, db_session)

UDNCrawler Methods:
    __init__(self, timeout: int = 5): Initializes the crawler with a default timeout for HTTP requests.
    startup(self, search_term: str) -> list[Headline]: Fetches news headlines for a given search term across multiple pages.
    get_headline(self, search_term: str, page: int | tuple[int, int]) -> list[Headline]: Fetches news headlines for specified pages.
    _fetch_news(self, page: int, search_term: str) -> list[Headline]: Helper method to fetch news headlines for a specific page.
    _create_search_params(self, page: int, search_term: str): Creates the parameters for the search request.
    _perform_request(self, params: dict): Performs the HTTP request to fetch news data.
    _parse_headlines(response): Parses the response to extract headlines.
    parse(self, url: str) -> News: Parses a news article from a given URL.
    _extract_news(soup, url: str) -> News: Extracts news details from the BeautifulSoup object.
    save(self, news: News, db: Session): Saves a news article to the database.
    _commit_changes(db: Session): Commits the changes to the database with error handling.
"""

from requests import Response
from bs4 import BeautifulSoup
from urllib.parse import quote
from requests.exceptions import RequestException
import requests
from sqlalchemy.orm import Session
from sentry_sdk import capture_exception
import logging

from src.services.logger import udn_crawler_logger
from .crawler_base import NewsCrawlerBase, Headline, News, NewsWithSummary
from src.news.models import NewsArticle
from .config import crawler_config
from .exceptions import (
    InvalidResponseException,
    ParsingException,
    DatabaseSaveException,
    SavingExistingNewsException,
    ExtractNewsException,
    InvalidHeadlineExceptions
)

class UDNCrawler(NewsCrawlerBase):
    CHANNEL_ID = 2

    def __init__(self, timeout: int = 5) -> None:
        self.news_website_url = crawler_config.UDN_API_URL  
        self.timeout = timeout

    def startup(self, search_term: str) -> list[Headline]:
        """
        Initializes the application by fetching news headlines for a given search term across multiple pages.
        This method is typically called at the beginning of the program when there is no data available,
        hence it fetches headlines from the first 10 pages.

        :param search_term: The term to search for in news headlines.
        :return: A list of Headline namedtuples containing the title and URL of news articles.
        :rtype: list[Headline]
        """
        try:
            headlines = self.get_headline(search_term, page=(1, 10))
            udn_crawler_logger.startup_success(search_term, count=len(headlines))
            return headlines
        except Exception as e:
            udn_crawler_logger.startup_failed(search_term, error=e)
            raise

    def get_headline(
        self, search_term: str, page: int | tuple[int, int]
    ) -> list[Headline]:

        # Calculate the range of pages to fetch news from.
        # If 'page' is a tuple, unpack it and create a range representing those pages (inclusive).
        # If 'page' is an int, create a list containing only that single page number.
        # page_range = range(*page) if isinstance(page, tuple) else [page]
        page_range = range(page[0], page[1] + 1) if isinstance(page, tuple) else [page]
        headlines = []
        for page_num in page_range:
            fetched_headlines = self._fetch_news(page=page_num, search_term=search_term)
            headlines.extend(fetched_headlines)
        return headlines

    def _fetch_news(self, page: int, search_term: str) -> list[Headline]:
        params = self._create_search_params(page=page, search_term=search_term)
        response = self._perform_request(params=params)
        return self._parse_headlines(response)

    def _create_search_params(self, page: int, search_term: str) -> dict:
        return {
            "page": page,
            "id": f"search:{quote(search_term)}",
            "channelId": self.CHANNEL_ID,
            "type": "searchword",
        }

    def _perform_request(self, url: str | None = None, params: dict | None = None) -> Response:
        if url is None:
            url = self.news_website_url
        try:
            if url is None:
                url = self.news_website_url
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except RequestException as e:
            logging.warning(f"[UDNCrawler] Failed to send request to udn api, {str(e)}")
            capture_exception(e)
            raise InvalidResponseException()
        
        return response

    @staticmethod
    def _parse_headlines(response: Response) -> list[Headline]:
        try:
            data = response.json()
            if "lists" not in data:
                raise InvalidHeadlineExceptions()
            processed_items = [
                {"title": item["title"], "url": item["titleLink"]}
                for item in data["lists"]
            ]
        
            return [Headline(**item) for item in processed_items]
        except (KeyError, ValueError, TypeError) as e:
            capture_exception(e)
            logging.warning(f"[UDNCrawler] Headlines parsing failed. error: {str(e)}")
            raise InvalidHeadlineExceptions()

    def _parse(self, url: str) -> News:
        logging.debug(f"[UDNCrawler] Parsing started, url: {url}")
        try:
            response = self._perform_request(url=url)
        except InvalidResponseException:
            logging.warning(f"[UDNCralwer] Failed to get response from udn")
            raise

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            news = self._extract_news(soup, url)
        except ExtractNewsException:
            logging.warning(f"[UDNCrawler] Failed to parse news, some error occured when extracting")
            raise ParsingException()

        logging.debug(f"[UDNCrawler] Parsing success, url: {url}")
        return news

    @staticmethod
    def _extract_news(soup: BeautifulSoup, url: str) -> News:
        try:
            logging.debug(f"[UDNCrawler] Extracting news content from: {url}")
            title = soup.find("h1", class_="article-content__title").text
            time = soup.find("time", class_="article-content__time").text
            content_section = soup.find("section", class_="article-content__editor")
            paragraphs = [
                p.text
                for p in content_section.find_all("p")
                if p.text.strip() != "" and "▪" not in p.text
            ]
            content = " ".join(paragraphs)

        except AttributeError as e:
            logging.warning(f"Failed to extract news. error: {str(e)}")
            capture_exception(e)
            raise ExtractNewsException()

        logging.debug(f"[UDNCrawler] Successfully extracted news. title: {title}")

        return News(
            title=title,
            url=url,
            time=time,
            content=content
        )
    
    def save(self, news: NewsWithSummary, db: Session):
        logging.debug(f"[UDNCrawler] Saving news article: {news.title}")
        existing_news = db.query(NewsArticle).filter_by(url=news.url).first()
        if existing_news:
            logging.warning(f"[UDNCrawler] News already exist, skipping. title: {news.title}")
            raise SavingExistingNewsException(news.url)

        new_article = NewsArticle(
            url=news.url,
            title=news.title,
            time=news.time,
            content=news.content,
            summary=news.summary,
            reason=news.reason,
        )

        db.add(new_article)
        self._commit_changes(db)
        logging.debug(f"[UDNCrawler] Successfully saved news. title: {news.title}")
        
    @staticmethod
    def _commit_changes(db: Session):
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            capture_exception(e)
            logging.warning(f"[UDNCrawler] Unable to commit changes into database, error: {str(e)}")
            raise DatabaseSaveException()
        finally:
            db.close()
