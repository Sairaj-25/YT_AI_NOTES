from yt_dlp import YoutubeDL
import os
import logging

logger = logging.getLogger(__name__)

MEDIA_ROOT = "media"

os.makedirs(MEDIA_ROOT, exist_ok=True)


def download_audio(link: str) -> str | None:
    try:
        ydl_opts = {
            "format": "worstaudio/worst",
            "outtmpl": os.path.join(MEDIA_ROOT, "%(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "quiet": True,
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            mp3_path = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"
            return mp3_path

    except Exception as e:
        logger.error(f"Audio download error: {e}")
        return None
