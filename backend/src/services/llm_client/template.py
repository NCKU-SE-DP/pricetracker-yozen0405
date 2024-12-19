from abc import ABC, abstractmethod
import json

from .base import MessageInterface, LLMClientBase
from .enum import PromptTemplate, RelevanceLevel

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
        response_data = {}
        if result:
            try:
                result = json.loads(result)
                response_data["summary"] = result["影響"]
                response_data["reason"] = result["原因"]
            except json.JSONDecodeError as e:
                response_data["error"] = f"JSONDecodeError: {str(e)}"
        return response_data

    def generate_summary(self, text: str) -> dict:
        """Generate a summary using the specified model."""
        messages = self._generate_messages(prompt=PromptTemplate.SUMMARY, text=text)
        result = self._generate_text(messages=messages)
        return self._parse_summary_result(result)

    def evaluate_relevance(self, text: str) -> RelevanceLevel:
        """Evaluate relevance using the specified model."""
        messages = self._generate_messages(prompt=PromptTemplate.RELEVANCE, text=text)
        result = self._generate_text(messages=messages)

        if result in RelevanceLevel._value2member_map_:
            return RelevanceLevel(result)
        else:
            raise ValueError(f"Unexpected relevance level: {result}")

    def extract_search_keywords(self, text: str) -> str:
        """Extract search keywords using the specified model."""
        messages = self._generate_messages(prompt=PromptTemplate.KEYWORDS, text=text)
        return self._generate_text(messages=messages)
    
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
            raise RuntimeError(f"Error generating text: {str(e)}")