from .logger_service import LogMessageInterface, LoggerService
from typing import Optional

class NewsLogMessages:
    def __init__(self):
        self.logger = LoggerService("news_service")

    def fetch_db_news_success(self, count: int):
        message = LogMessageInterface("Successfully fetched news articles in database", count=count)
        self.logger.log_info(message)

    def fetch_db_news_failed(self, error: Exception, article_id: Optional[int] = None):
        if (article_id):
            message = LogMessageInterface("Failed to fetch news articles in database", error=error)
        else:
            message = message = LogMessageInterface("Failed to fetch specific article in database", error=error, article_id=article_id)
        self.logger.log_error(message)

    def searching_udn_news(self):
        message = LogMessageInterface("Searching udn news")
        self.logger.log_info(message)

    def search_udn_success(self, title: str):
        message = LogMessageInterface("News has been searched successfly", title=title)
        self.logger.log_info(message)

    def search_udn_failed(self, url: str, error: Exception):
        message = LogMessageInterface("Failed to search news", url=url, error=error)
        self.logger.log_error(message)

    def added_high_relevance_article(self, title: str):
        message = LogMessageInterface("Processed and added high-relevance article", title=title)
        self.logger.log_info(message)

    def upvote_success(self, article_id: int, user_id: int):
        message = LogMessageInterface("Upvote successful", article_id=article_id, user_id=user_id)
        self.logger.log_info(message)

    def upvote_failed(self, article_id: int, user_id: int, error: Exception):
        message = LogMessageInterface("Upvote failed", article_id=article_id, user_id=user_id, error=str(error))
        self.logger.log_warning(message)

    def upvote_added(self, article_id: int, user_id: int):
        message = LogMessageInterface(
            "Upvote added successfully", article_id=article_id, user_id=user_id
        )
        self.logger.log_info(message)

    def upvote_removed(self, article_id: int, user_id: int):
        message = LogMessageInterface(
            "Upvote removed successfully", article_id=article_id, user_id=user_id
        )
        self.logger.log_info(message)

    def article_not_found(self, article_id: int, user_id: Optional[int] = None):
        message = LogMessageInterface(
            "Article not found", article_id=article_id, user_id=user_id
        )
        self.logger.log_warning(message)

    def get_upvote_count_success(self, article_id: int, user_id: int, upvote_count: int, has_voted: bool):
        message = LogMessageInterface(
                    "Failed to get upvote count", 
                    article_id=article_id, 
                    user_id=user_id, 
                    upvote_count=upvote_count, 
                    has_voted=has_voted
                )
        self.logger.log_info(message)

    def get_upvote_count_failed(self, article_id: int, user_id: int, error: Exception = None):
        message = LogMessageInterface("Failed to get upvote count", article_id=article_id, user_id=user_id, error=error)
        self.logger.log_error(message)

    def toggle_article_failed(self, article_id: int, user_id: int, error: Exception = None):
        message = LogMessageInterface("Failed to toggle article", article_id=article_id, user_id=user_id, error=error)
        self.logger.log_error(message)

    def error_processing_article(self, article_id: int, user_id: int, error: Exception = None):
        message = LogMessageInterface("Error processing article", article_id=article_id, user_id=user_id, error=str(error))
        self.logger.log_error(message)

news_logger = NewsLogMessages()
