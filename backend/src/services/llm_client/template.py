from abc import ABC, abstractmethod
import json

from .base import MessageInterface, LLMClientBase
from .enum import PromptTemplate, RelevanceLevel, ResultFields
from src.services.exceptions_handler import InternalServerErrorException, InvalidAiInputParamException
from src.services.logger import llm_client_logger

class LLMClientTemplate(LLMClientBase, ABC):
    """
    Base class for LLM clients using Template Method Pattern.
    Encapsulates shared logic for interacting with AI models.
    """

    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None  
        self.model = None
        self._initialize_client()

    def _initialize_client(self):
        config = self._create_config()
        self.model = self._get_model(config)
        self.client = self._get_client(config)

    @abstractmethod
    def _create_config(self):
        """Return the aisuite client configuration."""
        pass

    @abstractmethod
    def _get_model(self, config) -> str:
        """Return the model name in config."""
        pass

    @abstractmethod
    def _get_client(self, config):
        """Return the client in config."""
        pass

    @staticmethod
    def _generate_messages(prompt: PromptTemplate, text: str) -> MessageInterface:
        return MessageInterface(system_content=prompt.to_string(), user_content=text)
    
    @staticmethod 
    def _parse_summary_result(result: str) -> dict:
        """
        Parses the summary result JSON and extracts 'summary' and 'reason'.

        :param result: The JSON-formatted summary result string.
        :return: A dictionary with keys 'summary' and 'reason', or an empty dictionary if parsing fails.
        """
        try:
            result_json = json.loads(result)
            if ResultFields.SUMMARY_CH.value not in result_json or ResultFields.REASON_CH.value not in result_json:
                llm_client_logger.parse_summary_failed(summary=result)
                raise InvalidAiInputParamException()
            
            return {
                ResultFields.SUMMARY_EN.value: result_json[ResultFields.SUMMARY_CH.value],
                ResultFields.REASON_EN.value: result_json[ResultFields.REASON_CH.value]
            }
        except json.JSONDecodeError:
            llm_client_logger.parse_summary_failed(summary=result)
            raise InvalidAiInputParamException(result)

    def generate_summary(self, text: str) -> dict:
        """Generate a summary using the specified model."""
        try:
            messages = self._generate_messages(prompt=PromptTemplate.SUMMARY, text=text)
            result = self._generate_text(messages=messages)
            summary = self._parse_summary_result(result)
            llm_client_logger.summary_generate_success(text=text, summary=summary)
            return summary
        except Exception as e:
            llm_client_logger.summary_generate_failed(text=text, error=e)
            raise

    def evaluate_relevance(self, text: str) -> RelevanceLevel:
        """Evaluate relevance using the specified model."""
        try:
            messages = self._generate_messages(prompt=PromptTemplate.RELEVANCE, text=text)
            result = self._generate_text(messages=messages)

            if result in RelevanceLevel._value2member_map_:
                relevance = RelevanceLevel(result)
                llm_client_logger.relevance_evaluate_success(text=text, relevance=relevance.value)
                return RelevanceLevel(result)
            else:
                llm_client_logger.unexpected_relevance_level(result=result)
                raise InternalServerErrorException("Unxcepted relevance level")
        except Exception as e:
            llm_client_logger.relevance_evaluate_failed(text=text, error=e)
            raise

    def extract_search_keywords(self, text: str) -> str:
        """Extract search keywords using the specified model."""
        try:
            messages = self._generate_messages(prompt=PromptTemplate.KEYWORDS, text=text)
            keywords = self._generate_text(messages=messages)
            llm_client_logger.keywords_extracte_success(text=text, keywords=keywords)
            return keywords
        except Exception as e:
            llm_client_logger.keywords_extracte_failed(text=text, error=e)
            raise
    
    def _generate_text(self, messages: MessageInterface) -> str:
        """
        Shared method to generate text for both OpenAI and Anthropic clients.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages.to_dict,
            )
            return response.choices[0].message.content
        except Exception as e:
            llm_client_logger.generate_text_failed(e)
            raise InternalServerErrorException(e)
