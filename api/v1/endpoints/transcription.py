from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from services.audio_download_service import download_audio
from services.audio_transcribe_service import transcribe_audio_whisper

router = APIRouter(prefix="/yt", tags=["YT Transcription"])


class YTRequest(BaseModel):
    link: HttpUrl


@router.post("/process")
async def process_video(payload: YTRequest):
    file_path = download_audio(str(payload.link))

    if not file_path:
        raise HTTPException(400, "Audio download failed")

    transcript = transcribe_audio_whisper(file_path)

    return {"file_path": file_path, "trnascript": transcript}
