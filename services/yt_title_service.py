from yt_dlp import YoutubeDL
import logging

logger = logging.getLogger(__name__)

def get_yt_title(link: str) -> str | None:
    try:
        with YoutubeDL() as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get("title", "Unknown Title")
    except Exception as e:
        logger.error(f"Youtube title error: {e}")
        return None
