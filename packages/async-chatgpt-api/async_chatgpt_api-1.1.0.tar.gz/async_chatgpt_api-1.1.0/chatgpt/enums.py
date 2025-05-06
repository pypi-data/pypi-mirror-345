from enum import StrEnum


class OpenAIModels(StrEnum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4o_MINI = "gpt-4o-mini"


class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class BaseURL(StrEnum):
    OPENAI = "https://api.openai.com"


class Endpoint(StrEnum):
    CHAT_COMPLETION_V1 = "/v1/chat/completions"
