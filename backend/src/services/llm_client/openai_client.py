from .base import LLMClientBase
from .base import MessageInterface
from .openai_client_prompt import PromptTemplate
from .config import ai_config

from openai import OpenAI

class OpenAIClient(LLMClientBase):
    def __init__(self, _api_key: str = None, _model: str = None) -> None:
        self._api_key = _api_key or ai_config.OPEN_AI_KEY
        self._model = _model or ai_config.OPEN_AI_MODEL

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
    def _generate_messages(prompt: str, text: str) -> MessageInterface:
        return MessageInterface(system_content=prompt, user_content=text)

    def _generate_text(self, messages: MessageInterface) -> str:
        formatted_messages = messages.to_dict
        try:
            completion = OpenAI(api_key=self._api_key).chat.completions.create(
                model=self._model,
                messages=formatted_messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to call OpenAI API: {str(e)}")
