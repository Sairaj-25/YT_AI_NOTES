import asyncio
import markdown
from fastapi import APIRouter, Request, Form, Depends
from pathlib import Path
import logging
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.yt_title_service import get_yt_title
from services.audio_download_service import download_audio
from services.audio_transcribe_service import transcribe_audio_whisper
from services.generate_notes_service import generate_note_from_transcription

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
    link: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("Received audio upload: link=%s", link)
    
    # 1. Validate Request
    if not link:
        return HTMLResponse("<div class='text-danger'>Youtube link is required.</div>")

    # 2. Get title
    title = get_yt_title(link)
    if not title:
        return HTMLResponse(
            "<div class='text-danger'>Failed to fetch YouTube title.</div>"
        )

    # 3. Download audio
    file_path = download_audio(link)
    if not file_path:
        return HTMLResponse("<div class='text-danger'>Failed to download audio.</div>")

    loop = asyncio.get_running_loop()

    # 4. transcribe
    transcription: str = await loop.run_in_executor(
        None, transcribe_audio_whisper, file_path
    )
    if not transcription or "Failed" in transcription:
        return HTMLResponse("<div class='text-danger'>Failed to get transcript.</div>")

    # 5. Generate Note
    note_content = generate_note_from_transcription(transcription)
    if not note_content or "Error" in note_content:
        return HTMLResponse(f"<div class='text-danger'>{note_content}</div>")

    # 6. Save to db (Saving raw markdown)
    note = Notes(youtube_link=link, content=note_content)

    db.add(note)
    await db.commit()
    await db.refresh(note)

    # 7. Return template with raw markdown
    return templates.TemplateResponse(
        request, "partials/blog_result.html", {"title": title, "note_content": note_content}
    )