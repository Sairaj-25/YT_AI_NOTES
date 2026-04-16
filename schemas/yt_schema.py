from pydantic import BaseModel, HttpUrl


class yt_TitleRequest(BaseModel):
    yt_link: HttpUrl


class yt_TitleResponse(BaseModel):
    title: str
    success: bool
