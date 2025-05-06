from enum import StrEnum
from typing import Any, Literal, TypeAlias, TypedDict, Optional


GeneralDict: TypeAlias = dict[str, Any]


class MessageDictT(TypedDict):
    role: str
    content: str


class Role(StrEnum):
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"


class ContentT(TypedDict):
    type: Literal["text"]
    text: str


class MessageT(TypedDict):
    role: Role
    content: list[ContentT]


class RequestDataT(TypedDict):
    model: Optional[str]
    temperature: Optional[float]
    messages: list[MessageT]
