from pydantic import BaseModel, HttpUrl
from typing import Optional

class AudioDownloadRequest(BaseModel):
    link: HttpUrl

class AudioDownloadResponse(BaseModel):
    file_path: set
    success: bool