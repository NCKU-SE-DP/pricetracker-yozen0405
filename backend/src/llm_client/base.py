import abc
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MessageInterface(BaseModel):
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
    _api_key = str
    _model = str
    
    @abc.abstractmethod
    def evaluate_relevance(self, text: str) -> str:
        """
        Evaluate the relevance of the provided text to a specific context.

        :param text: A string containing the text to be evaluated.
        :type text: str

        :return: A string indicating the relevance level: 'high', 'medium', or 'low'.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def generate_summary(self, text: str) -> Dict[str, str]:
        """
        Generate a summary of the provided text, including its impact and reasons.

        :param text: A string containing the content to summarize.
        :type text: str

        :return: A dictionary with two keys:
                 - 'impact': A string describing the impact.
                 - 'reason': A string explaining the reasons.
        :rtype: Dict[str, str]
        """
        pass

    @abc.abstractmethod
    def extract_search_keywords(self, text: str) -> str:
        """
        Extract search keywords from the provided text.

        :param text: A string containing the input text from which keywords are to be extracted.
        :type text: str

        :return: A string of space-separated keywords extracted from the input text.
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def _generate_text(self, messages: List[Dict[str, Any]]) -> str:
        """
        Interact with the underlying LLM API to generate a text response.

        :param messages: A list of dictionaries, where each dictionary represents a message
                         with keys 'role' (e.g., 'system', 'user') and 'content' (the text message).
        :type messages: List[Dict[str, Any]]

        :return: A string containing the generated response from the LLM API.
        :rtype: str
        """
        pass