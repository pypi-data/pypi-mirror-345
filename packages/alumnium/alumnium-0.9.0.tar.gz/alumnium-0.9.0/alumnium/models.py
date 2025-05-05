from enum import Enum
from os import environ


class Model(Enum):
    AZURE_OPENAI = "gpt-4o-mini"  # 2024-07-18
    ANTHROPIC = "claude-3-haiku-20240307"
    AWS_ANTHROPIC = "anthropic.claude-3-haiku-20240307-v1:0"
    AWS_META = "us.meta.llama3-2-90b-instruct-v1:0"
    DEEPSEEK = "deepseek-chat"
    GOOGLE = "gemini-2.0-flash-001"
    OLLAMA = "mistral-small3.1"
    OPENAI = "gpt-4o-mini-2024-07-18"

    @classmethod
    def load(cls):
        return cls[environ.get("ALUMNIUM_MODEL", "openai").upper()]
