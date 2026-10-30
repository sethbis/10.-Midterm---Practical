from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    original_url: HttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str


class UrlInfoResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: str
