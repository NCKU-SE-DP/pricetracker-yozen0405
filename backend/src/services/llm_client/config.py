from abc import ABC, abstractmethod

class LLMConfig(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    def get_config_dict(self):
        """Encapsulate configuration as a dictionary."""
        pass

class OpenAIConfig(LLMConfig):
    MODEL = "openai:gpt-4o"

    def __init__(self, api_key: str):
        super().__init__(api_key, self.MODEL)

    def get_config_dict(self):
        return {"openai": {"api_key": self.api_key}}

class AnthropicConfig(LLMConfig):
    MODEL = "anthropic:claude-3-5-sonnet-20240620"

    def __init__(self, api_key: str):
        super().__init__(api_key, self.MODEL)

    def get_config_dict(self):
        return {"anthropic": {"api_key": self.api_key}}