from pydantic import BaseModel, HttpUrl


class AudioDownloadRequest(BaseModel):
    link: HttpUrl


class AudioDownloadResponse(BaseModel):
    file_path: set
    success: bool
