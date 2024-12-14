from .logger_service import LoggerService, LogMessageInterface

class LLMClientLogMessages:
    def __init__(self):
        self.logger = LoggerService("llm_client_service")

    def summary_generate_success(self, text: str, summary: dict):
        message = LogMessageInterface("Generated summary successfully", input_text=text, summary=summary)
        self.logger.log_debug(message)

    def summary_generate_failed(self, text: str, error: Exception):
        message = LogMessageInterface("Generated summary", input_text=text, error=error)
        self.logger.log_error(message)

    def parse_summary_failed(self, summary: str):
        message = LogMessageInterface("Failed to parse summary", summary=summary)
        self.logger.log_error(message)

    def relevance_evaluate_success(self, text: str, relevance: str):
        message = LogMessageInterface("Relevance evaluated successfully", input_text=text, relevance=relevance)
        self.logger.log_debug(message)

    def relevance_evaluate_failed(self, text: str, error: Exception):
        message = LogMessageInterface("Relevance evaluate failed", input_text=text, error=error)
        self.logger.log_error(message)

    def keywords_extracte_success(self, text: str, keywords: str):
        message = LogMessageInterface("Keywords extracted successfully", input_text=text, keywords=keywords)
        self.logger.log_debug(message)

    def keywords_extracte_failed(self, text: str, error: Exception):
        message = LogMessageInterface("Keywords extract failed", input_text=text, error=error)
        self.logger.log_error(message)

    def unexpected_relevance_level(self, result: str):
        message = LogMessageInterface("Unexpected relevance level returned", result=result)
        self.logger.log_error(message)

    def generate_text_failed(self, error: Exception):
        message = LogMessageInterface("Failed to interact with ai client", error)
        self.logger.log_error(message)

llm_client_logger = LLMClientLogMessages()