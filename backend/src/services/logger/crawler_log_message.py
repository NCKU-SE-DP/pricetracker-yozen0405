from .logger_service import LoggerService, LogMessageInterface

class UDNCrawlerLogMessages:
    def __init__(self):
        self.logger = LoggerService("udn_crawler_service")

    def fetch_headline_start(self, search_term: str, pages: list[int]):
        message = LogMessageInterface(
            "Fetching headlines started", search_term=search_term, pages=pages
        )
        self.logger.log_info(message)

    def fetch_headline_success(self, search_term: str, total_count: int):
        message = LogMessageInterface(
            "Fetching headlines completed successfully", 
            search_term=search_term, 
            total_count=total_count
        )
        self.logger.log_info(message)

    def fetch_headline_failed(self, search_term: str, error: Exception):
        message = LogMessageInterface(
            "Fetching headlines failed", 
            search_term=search_term, 
            error=error
        )
        self.logger.log_error(message)

    def fetch_page_start(self, search_term: str, page: int):
        message = LogMessageInterface(
            "Fetching page started", search_term=search_term, page=page
        )
        self.logger.log_debug(message)

    def fetch_page_success(self, search_term: str, page: int, count: int):
        message = LogMessageInterface(
            "Fetching page completed successfully", 
            search_term=search_term, 
            page=page, 
            count=count
        )
        self.logger.log_info(message)

    def startup_success(self, search_term: str, count: int):
        message = LogMessageInterface("Successfully fetched headlines", search_term=search_term, count=count)
        self.logger.log_info(message)

    def startup_failed(self, search_term: str, error: Exception):
        message = LogMessageInterface("Failed to fetch headlines", search_term=search_term, error=error)
        self.logger.log_error(message)

    def parse_news_start(self, url: str):
        message = LogMessageInterface("Started parsing news article", url=url)
        self.logger.log_debug(message)

    def parse_news_success(self, url: str):
        message = LogMessageInterface("Successfully parsed news article", url=url)
        self.logger.log_info(message)

    def parse_news_failed(self, url: str, error: Exception):
        message = LogMessageInterface("Failed to parse news article", url=url, error=error)
        self.logger.log_error(message)

    def extract_news_success(self, url: str, title: str):
        message = LogMessageInterface("Extract news article succuessfly", url=url, title=title)
        self.logger.log_debug(message)

    def extract_news_failed(self, url: str, error: Exception):
        message = LogMessageInterface("Failed to extract news article", url=url, error=error)
        self.logger.log_error(message)

    def save_news_success(self, url: str):
        message = LogMessageInterface("Successfully saved news article", url=url)
        self.logger.log_info(message)

    def save_news_skipped(self, url: str):
        message = LogMessageInterface("Skipped saving news article (already exists)", url=url)
        self.logger.log_debug(message)

    def save_news_failed(self, url: str, error: Exception):
        message = LogMessageInterface("Failed to save news article", url=url, error=error)
        self.logger.log_error(message)

    def request_failed(self, params: dict, error: Exception):
        message = LogMessageInterface("HTTP request failed", params=params, error=error)
        self.logger.log_error(message)

    def request_success(self, url: str, params: dict):
        message = LogMessageInterface("HTTP request success", url=url, params=params)
        self.logger.log_debug(message)

udn_crawler_logger = UDNCrawlerLogMessages()