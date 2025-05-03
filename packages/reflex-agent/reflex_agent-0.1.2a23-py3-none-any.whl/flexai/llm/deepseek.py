import os
from dataclasses import dataclass, field, InitVar
from flexai.llm.openai import OpenAIClient


@dataclass(frozen=True)
class DeepseekClient(OpenAIClient):
    """Client for the Deepseek API."""

    # The API key to use for interacting with the model.
    api_key: InitVar[str] = field(default=os.environ.get("DEEPSEEK_API_KEY", ""))

    # The base URL for the Deepseek API.
    base_url: InitVar[str] = field(
        default=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.ai/v1")
    )

    # The model to use for the client.
    model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3")
