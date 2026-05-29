import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
FILENAME_MAX_LENGTH = 180


def _safe_transcription_filename(title: str) -> str:
    safe_title = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "", title).strip()
    safe_title = re.sub(r"\s+", " ", safe_title).rstrip(". ")
    if not safe_title:
        safe_title = "transcription"

    return f"{safe_title[:FILENAME_MAX_LENGTH]}.txt"


def save_transcription_text(transcription: str, yt_title: str) -> str | None:
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / _safe_transcription_filename(yt_title)
        output_path.write_text(transcription, encoding="utf-8")
        logger.info("Saved transcription text file: %s", output_path)
        return str(output_path)

    except OSError as e:
        logger.error(
            "Failed to save transcription for %s: %s", yt_title, e, exc_info=True
        )
        return None
