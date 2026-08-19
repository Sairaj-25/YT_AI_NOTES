import logging
import os
from dataclasses import dataclass
from pathlib import Path

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

MEDIA_ROOT = "media"


os.makedirs(MEDIA_ROOT, exist_ok=True)


@dataclass(frozen=True)
class AudioDownload:
    file_path: str
    title: str


def downloaded_file_path(info: dict, ydl: YoutubeDL) -> str | None:
    requested_downloads = info.get("requested_downloads") or []
    for download in requested_downloads:
        file_path = download.get("filepath")
        if file_path:
            return file_path

    return ydl.prepare_filename(info)


def download_audio_with_metadata(link: str) -> AudioDownload | None:
    try:
        ydl_opts = {
            # m4a (AAC) and webm (Opus) are the only audio formats YouTube serves.
            # faster-whisper accepts both directly — no WAV conversion needed.
            "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best",
            "outtmpl": os.path.join(MEDIA_ROOT, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "retries": 5,
            "fragment_retries": 5,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = downloaded_file_path(info, ydl)
            if not file_path:
                return None

            return AudioDownload(
                file_path=file_path,
                title=info.get("title") or "Unknown Title",
            )

    except Exception as e:
        logger.error(f"Audio download error: {e}")
        return None


def download_audio(link: str) -> str | None:
    download = download_audio_with_metadata(link)
    if not download:
        return None

    return download.file_path


def delete_downloaded_audio(file_path: str) -> bool:
    try:
        media_root = Path(MEDIA_ROOT).resolve()
        audio_path = Path(file_path).resolve()

        if not audio_path.is_relative_to(media_root):
            logger.warning("Skipping delete outside media directory: %s", file_path)
            return False

        if not audio_path.exists():
            logger.info("Audio file already removed: %s", audio_path)
            return False

        audio_path.unlink()
        logger.info("Deleted transcribed audio file: %s", audio_path)
        return True

    except OSError as e:
        logger.error("Audio delete error for %s: %s", file_path, e, exc_info=True)
        return False
