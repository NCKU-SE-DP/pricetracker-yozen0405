import abc
from pydantic import BaseModel, Field
from typing import List

class MessageInterface(BaseModel):
    """
    Represents the structure of a message sent to or received from the LLM API.
    """
    role: str = Field(
        default=...,
        example="system",
        description="The role of the message sender, e.g., 'system', 'user', or 'assistant'."
    )
    content: str = Field(
        default=...,
        example="Describe the impact of the news.",
        description="The content of the message."
    )
    

class LLMClientBase(metaclass=abc.ABCMeta):
    """
    Abstract base class defining the interface for an LLM client.
    Subclasses must implement methods to evaluate text relevance, generate summaries, 
    extract keywords, and interact with the underlying LLM API.
    """
    _api_key = str
    _model = str
    
    @abc.abstractmethod
    def evaluate_relevance(self, text: str) -> str:
        """
        Evaluates the relevance of the provided text to a specific context.

        :param text: The input text to evaluate.
        :type text: str

        :return: The relevance level, which can be 'high', 'medium', or 'low'.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def generate_summary(self, text: str) -> str:
        """
        Generates a summary for the provided text, including its impact and reasons.

        :param text: The input text to summarize.
        :type text: str

        :return: A JSON-formatted string containing the impact and reason.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def extract_search_keywords(self, text: str) -> str:
        """
        Extracts the most relevant search keywords from the input text.

        :param text: The input text from which keywords are extracted.
        :type text: str

        :return: A string of space-separated keywords extracted from the input text.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def _generate_text(self, messages: List[MessageInterface]) -> str:
        """
        Interacts with the underlying LLM API to generate a response based on the provided messages.

        :param messages: A list of MessageInterface instances representing the conversation context.
        :type messages: List[MessageInterface]

        :return: The generated text response from the LLM API.
        :rtype: str
        """
        pass