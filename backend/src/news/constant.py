from enum import Enum

class AiModelType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

ARTICLE_ID_START = 1000000