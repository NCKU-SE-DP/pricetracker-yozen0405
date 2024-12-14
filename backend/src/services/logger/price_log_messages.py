from .logger_service import LoggerService, LogMessageInterface

class PriceLogMessages:
    def __init__(self):
        self.logger = LoggerService("price_service")

    def sended_request(self, url: str, params: dict):
        message = LogMessageInterface(message="Price API request initiated", url=url, params=params)
        self.logger.log_info(message)

    def response_success(self):
        message = LogMessageInterface(message="Price API response received successfully")
        self.logger.log_info(message)

    def no_resource_found(self, url: str, params: dict):
        message = LogMessageInterface(message="No resources found for the query", url=url, params=params)
        self.logger.log_warning(message)

    def internal_error(self, error: Exception):
        message = LogMessageInterface(message="Internal server error while accessing Price API", error=str(error))
        self.logger.log_error(message)

price_logger = PriceLogMessages()