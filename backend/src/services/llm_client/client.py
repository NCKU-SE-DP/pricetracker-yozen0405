from .config import OpenAIConfig, AnthropicConfig
from .template import LLMClientTemplate
import aisuite as ai

# OpenAI Client Implementation
class OpenAIClient(LLMClientTemplate):
    """
    Implementation for OpenAI API using aisuite.
    """
    def _create_config(self):
        return OpenAIConfig(self.api_key)

    def _get_model(self, config: OpenAIConfig) -> str:
        return config.model
    
    def _get_client(self, config: OpenAIConfig):
        return ai.Client(config.get_config_dict())

# Anthropic Client Implementation
class AnthropicClient(LLMClientTemplate):
    """
    Implementation for Anthropic API using aisuite.
    """

    def _create_config(self):
        return AnthropicConfig(self.api_key)

    def _get_model(self, config: AnthropicConfig) -> str:
        return config.model
    
    def _get_client(self, config: AnthropicConfig):
        return ai.Client(config.get_config_dict())