import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
from services.audio_download_service import delete_downloaded_audio, download_audio
from services.audio_transcribe_service import transcribe_audio_whisper

router = APIRouter(prefix="/yt", tags=["YT Transcription"])


class YTRequest(BaseModel):
    link: HttpUrl


@router.post("/process")
async def process_video(payload: YTRequest, background_tasks: BackgroundTasks):
    file_path: str | None = None

    try:
        loop = asyncio.get_running_loop()
        file_path = await loop.run_in_executor(None, download_audio, str(payload.link))

        if not file_path:
            raise HTTPException(400, "Audio download failed")

        transcript = await loop.run_in_executor(
            None, transcribe_audio_whisper, file_path
        )

        return {"file_path": file_path, "trnascript": transcript}

    finally:
        if file_path:
            background_tasks.add_task(delete_downloaded_audio, file_path)
