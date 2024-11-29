from .base import LLMClientBase
from .base import MessageInterface
from .openai_client_prompt import PromptTemplate

from typing import Any, Dict, List
import openai
import os
import json

class OpenAIClient(LLMClientBase):
    def __init__(self, _api_key: str, _model: str = None) -> None:
        self._api_key = _api_key
        self._model = _model or os.getenv("AI_OPEN_AI_MODEL")

    def generate_summary(self, text: str) -> str: 
        messages = self._generate_messages(prompt=PromptTemplate.summary(), text=text)

        response_text = self._generate_text(messages=messages)
        return response_text
    
    def evaluate_relevance(self, text: str) -> str:
        messages = self._generate_messages(prompt=PromptTemplate.relevance(), text=text)
        print(messages)
        return self._generate_text(messages=messages)
    
    def extract_search_keywords(self, text: str) -> str:
        messages = self._generate_messages(prompt=PromptTemplate.keywords(), text=text)

        return self._generate_text(messages=messages)
    
    @staticmethod
    def _generate_messages(prompt: str, text: str) -> List[MessageInterface]:
        return [
            MessageInterface(role="system", content=prompt),
            MessageInterface(role="user", content=text)
        ]

    def _generate_text(self, messages: List[MessageInterface]) -> str:
        formatted_messages = [message.dict() for message in messages]
        try:
            response = openai(api_key=self._api_key).ChatCompletion.create(
                model=self._model,
                messages=formatted_messages
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Failed to call OpenAI API: {str(e)}")
