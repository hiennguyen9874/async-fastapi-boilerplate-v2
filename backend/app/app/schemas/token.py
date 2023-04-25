from pydantic import BaseModel

__all__ = ["Token", "TokenPayload"]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: int | None = None
