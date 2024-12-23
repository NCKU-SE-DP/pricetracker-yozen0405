from enum import Enum

class AiModelType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"