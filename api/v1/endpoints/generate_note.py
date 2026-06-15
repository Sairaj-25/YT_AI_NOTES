import asyncio
from fastapi import APIRouter, BackgroundTasks, Request, Form, Depends
from pathlib import Path
import logging
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.audio_download_service import (
    delete_downloaded_audio,
    download_audio_with_metadata,
)
from services.audio_transcribe_service import (
    transcribe_audio_whisper,
    transcription_succeeded,
)
from services.generate_notes_service import generate_note_from_transcription
from services.youtube_url_service import normalize_youtube_url
from services.transcription_output_service import save_transcription_text

from models.db_models import Notes

router = APIRouter(prefix="/note", tags=["Note"])

logger = logging.getLogger(__name__)

# FIX: Go up 4 parents to reach the project root:
# api/v1/endpoints/generate_note.py -> endpoints -> v1 -> api -> YT_AI_NOTES (Root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# Now it correctly points to: D:\GitHub Projects\FastApi\YT_AI_NOTES\templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.post("/generate", response_class=HTMLResponse)
async def generate_note(
    request: Request,
    background_tasks: BackgroundTasks,
    link: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Received audio upload: link=%s", link)
    file_path: str | None = None

    try:
        # 1. Validate Request
        if not link:
            return HTMLResponse(
                "<div class='text-danger'>Youtube link is required.</div>",
                background=background_tasks,
            )

        # 1b. Normalise the URL so that youtu.be/X, watch?v=X, /shorts/X, etc.
        #     all map to the same canonical key: https://www.youtube.com/watch?v=X
        link = normalize_youtube_url(link)

        # 2. Cache check — skip the entire pipeline if this link was already processed.
        #    Query the Notes table by youtube_link before any expensive I/O.
        existing_note = await db.scalar(
            select(Notes).where(Notes.youtube_link == link).limit(1)
        )
        if existing_note:
            logger.info("Cache hit for link=%s — returning saved note.", link)
            return templates.TemplateResponse(
                request,
                "partials/blog_result.html",
                {
                    "title": existing_note.title or "YouTube Notes",
                    "note_content": existing_note.content,
                },
                background=background_tasks,
            )

        loop = asyncio.get_running_loop()

        # 3. Download audio and reuse the same metadata for the title.
        download = await loop.run_in_executor(None, download_audio_with_metadata, link)
        if not download:
            return HTMLResponse(
                "<div class='text-danger'>Failed to download audio.</div>",
                background=background_tasks,
            )
        file_path = download.file_path
        title = download.title

        # 4. Transcribe
        transcription: str = await loop.run_in_executor(
            None, transcribe_audio_whisper, file_path
        )
        if not transcription_succeeded(transcription):
            return HTMLResponse(
                "<div class='text-danger'>Failed to get transcript.</div>",
                background=background_tasks,
            )

        # 5. Generate Note
        note_content = await loop.run_in_executor(
            None, generate_note_from_transcription, transcription
        )
        if not note_content or "Error" in note_content:
            return HTMLResponse(
                f"<div class='text-danger'>{note_content}</div>",
                background=background_tasks,
            )
        background_tasks.add_task(save_transcription_text, transcription, title)

        # 6. Save to db (Saving raw markdown + title for future cache hits)
        note = Notes(youtube_link=link, title=title, content=note_content)

        db.add(note)
        await db.commit()
        await db.refresh(note)

        # 7. Return template with raw markdown
        return templates.TemplateResponse(
            request,
            "partials/blog_result.html",
            {"title": title, "note_content": note_content},
            background=background_tasks,
        )

    finally:
        if file_path:
            background_tasks.add_task(delete_downloaded_audio, file_path)
