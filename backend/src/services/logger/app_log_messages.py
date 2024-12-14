from .logger_service import LoggerService, LogMessageInterface

class AppLogMessages:
    def __init__(self):
        self.logger = LoggerService("app_service")

    def app_startup(self):
        message = LogMessageInterface(message="Application startup initiated")
        self.logger.log_info(message)

    def app_shutdown(self):
        message = LogMessageInterface(message="Application shutdown initiated")
        self.logger.log_info(message)

    def scheduler_started(self):
        message = LogMessageInterface(message="Scheduler started")
        self.logger.log_info(message)

    def scheduler_shutdown(self):
        message = LogMessageInterface(message="Scheduler shut down")
        self.logger.log_info(message)

    def fetch_news_job_started(self):
        message = LogMessageInterface(message="Fetch news job started")
        self.logger.log_error(message)

    def fetch_news_job_completed(self):
        message = LogMessageInterface(message="Fetch news job completed")
        self.logger.log_info(message)

    def fetch_news_job_failed(self, error: Exception):
        message = LogMessageInterface(message="Fetch news job failed", error=str(error))
        self.logger.log_error(message)

    def exception_occurred(self, path: str, method: str, error: str):
        message = LogMessageInterface(message="User registered successfully!", path=path, method=method, error=error)
        self.logger.log_error(message)

app_logger = AppLogMessages()