from typing import Optional, Union
from pydantic import BaseModel


class GeminiLLMToolRequest(BaseModel):
    api_key: str
    user_prompt: str
    system_prompt: str
    temperature: float = 0.7
    top_p: float = 0.9
    max_output_tokens: int = 2048
    max_retries: int = 100
    use_memory: bool = True
    refresh_chats: bool = False
    desired_json_response: Optional[dict | None] = None


class GeminiLLMToolResponse(BaseModel):
    input: str
    output: Union[str, dict]
    time_taken: int
    response_token: int
