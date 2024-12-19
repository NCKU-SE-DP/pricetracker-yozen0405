from pydantic import BaseModel
from .enums import AiModelType

class PromptRequest(BaseModel):
    prompt: str

class NewsSumaryRequestSchema(BaseModel):
    content: str

class NewsSumaryCustomModelSchema(BaseModel):
    content: str
    ai_model: AiModelType