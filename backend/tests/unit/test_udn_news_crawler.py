import unittest
from unittest.mock import patch, MagicMock
from requests.models import Response
from sqlalchemy.orm import Session
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

from src.services.crawler.udn_crawler import UDNCrawler, NewsWithSummary
from src.services.crawler.exceptions import (
    DomainMismatchException, 
    InvalidHeadlineExceptions, 
    InvalidResponseException, 
    ExtractNewsException, 
    SavingExistingNewsException,
    DatabaseSaveException
)

class TestUDNCrawler(unittest.TestCase):

    def setUp(self):
        self.scraper = UDNCrawler(timeout=5)

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_perform_request_success(self, mock_get):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.scraper._perform_request(params={"page": 1, "id": "search:technology"})
        self.assertEqual(response, mock_response)
        mock_get.assert_called_once()

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_perform_request_failure(self, mock_get):
        mock_get.side_effect = Exception("Network Error")
        with self.assertRaises(Exception):
            self.scraper._perform_request(params={"page": 1, "id": "search:technology"})

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_fetch_news_data(self, mock_get):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lists": [{"title": "Test News", "titleLink": "https://udn.com/news/test-news"}]
        }
        mock_get.return_value = mock_response

        headlines = self.scraper._fetch_news(page=1, search_term="technology")
        self.assertEqual(len(headlines), 1)
        self.assertEqual(headlines[0].title, "Test News")
        self.assertEqual(headlines[0].url, "https://udn.com/news/test-news")

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_parse_news(self, mock_get):
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.text = """
            <html>
                <h1 class="article-content__title">Test Title</h1>
                <time class="article-content__time">2023-09-08T00:00:00</time>
                <section class="article-content__editor">
                    <p>Content paragraph 1.</p>
                    <p>Content paragraph 2.</p>
                </section>
            </html>
        """
        mock_get.return_value = mock_response

        news = self.scraper.validate_and_parse("https://udn.com/news/test-news")
        self.assertEqual(news.title, "Test Title")
        self.assertEqual(news.time, "2023-09-08T00:00:00")
        self.assertEqual(news.content, "Content paragraph 1. Content paragraph 2.")

    def test_create_search_params(self):
        params = self.scraper._create_search_params(page=1, search_term="technology")
        self.assertEqual(params["page"], 1)
        self.assertEqual(params["id"], "search:technology")
        self.assertEqual(params["channelId"], 2)

    @patch("src.services.crawler.udn_crawler.Session")
    def test_save_news(self, mock_session):
        mock_db = MagicMock(spec=Session)
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        news = NewsWithSummary(
            title="Test Title",
            url="https://udn.com/news/test-news",
            time="2023-09-08T00:00:00",
            content="Test Content",
            summary="Test Summary",
            reason="Test Reason",
        )
        self.scraper.save(news, mock_db)

        mock_db.add.assert_called_once()
        self.assertEqual(mock_db.add.call_args[0][0].title, "Test Title")
        mock_db.commit.assert_called_once()

    def test_is_valid_url(self):
        valid_url = "https://udn.com/news/test-news"
        invalid_url = "https://example.com/news/test-news"

        self.assertTrue(self.scraper._is_valid_url(valid_url))
        self.assertFalse(self.scraper._is_valid_url(invalid_url))

    def test_parse_invalid_domain(self):
        invalid_url = "https://example.com/news/test-news"
        with self.assertRaises(DomainMismatchException):
            self.scraper.validate_and_parse(invalid_url)

class TestUDNCrawlerExceptions(unittest.TestCase):

    def setUp(self):
        self.scraper = UDNCrawler(timeout=5)

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_perform_request_exception(self, mock_get):
        """
        Test the behavior of the _perform_request method when a RequestException occurs.
        """
        mock_get.side_effect = RequestException("Mocked Network Error")
        with self.assertRaises(InvalidResponseException):
            self.scraper._perform_request()

        mock_get.assert_called_once()

    def test_parse_headlines_key_error(self):
        """
        Test the behavior of the _parse_headlines method when the 'lists' key is missing in the JSON response.
        """
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        with self.assertRaises(InvalidHeadlineExceptions):
            self.scraper._parse_headlines(mock_response)

    def test_extract_news_exception(self):
        """
        Test the behavior of the _extract_news method when the HTML structure is missing.
        """
        invalid_html = "<html></html>"
        soup = BeautifulSoup(invalid_html, "html.parser")

        with self.assertRaises(ExtractNewsException): 
            self.scraper._extract_news(soup, url="https://udn.com/news/test-news")

    @patch("src.services.crawler.udn_crawler.Session")
    def test_save_existing_news_exception(self, mock_session):
        """
        Test the behavior of the save method when a news article with the same URL already exists in the database.
        """
        mock_db = MagicMock(spec=Session)
        mock_db.query.return_value.filter_by.return_value.first.return_value = True

        news = NewsWithSummary(
            title="Existing News Title",
            url="https://udn.com/news/existing-news",
            time="2023-09-08T00:00:00",
            content="Existing news content.",
            summary="Existing summary.",
            reason="Existing reason."
        )
        with self.assertRaises(SavingExistingNewsException):
            self.scraper.save(news, mock_db)

    @patch("src.services.crawler.udn_crawler.Session")
    def test_save_commit_exception(self, mock_session):
        """
        Test the behavior of the save method when the database commit fails.
        """
        mock_db = MagicMock(spec=Session)
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.add.side_effect = None
        mock_db.commit.side_effect = Exception("Database Commit Error")

        news = MagicMock()
        with self.assertRaises(DatabaseSaveException): 
            self.scraper.save(news, mock_db)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.rollback.assert_called_once()

    @patch("src.services.crawler.udn_crawler.requests.get")
    def test_parse_news_request_exception(self, mock_get):
        """
        Test the behavior of the _parse method when a network request exception occurs.
        """
        mock_get.side_effect = RequestException("Mocked Network Error")

        with self.assertRaises(InvalidResponseException):
            self.scraper._parse("https://udn.com/news/test-news")

        mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()