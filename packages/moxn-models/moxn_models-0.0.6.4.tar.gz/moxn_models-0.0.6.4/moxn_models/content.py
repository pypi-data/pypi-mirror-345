from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    SCHEMA = "schema"


class Provider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"


class Author(Enum):
    HUMAN = "human"
    MACHINE = "machine"


class SignedUrlContentRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    key: str
    ttl_seconds: int = 3600


class SignedUrlContentResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    signed_url: str
    expiration: datetime
    message: str = "Signed URL generated successfully"
