import abc
from pydantic import BaseModel, Field
from typing import List

class MessageInterface(BaseModel):
    """
    Represents the structure of a message sent to the LLM API.
    """
    system_content: str = Field(...)
    user_content: str = Field(...)

    @property
    def to_dict(self):
        value = [
            {"role": "system", "content": f"{self.system_content}"},
            {"role": "user", "content": f"{self.user_content}"},
        ]
        return value
    

class LLMClientBase(metaclass=abc.ABCMeta):
    """
    Abstract base class defining the interface for an LLM client.
    """
    _api_key = str
    _model = str    

    @abc.abstractmethod
    def _generate_text(self, messages: MessageInterface) -> str:
        """
        Interacts with the underlying LLM API to generate a response based on the provided messages.

        :param messages: A list of MessageInterface instances representing the conversation context.
        :type messages: MessageInterface

        :return: The generated text response from the LLM API.
        :rtype: str
        """
        pass