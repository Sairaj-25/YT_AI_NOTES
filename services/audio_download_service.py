import logging
import os
from dataclasses import dataclass
from pathlib import Path

from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

MEDIA_ROOT = "media"
AUDIO_FORMAT = "bestaudio[ext=wav]/worstaudio/worst"

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
            "format": AUDIO_FORMAT,
            "outtmpl": os.path.join(MEDIA_ROOT, "%(title)s.%(ext)s"),
            "noplaylist": True,
            "quiet": True,
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
