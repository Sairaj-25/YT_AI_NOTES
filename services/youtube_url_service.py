"""
youtube_url_service.py
----------------------
Utility for normalising YouTube URLs so that different URL formats pointing
to the same video are treated as identical cache keys.

Supported input formats
-----------------------
  https://www.youtube.com/watch?v=VIDEO_ID
  https://youtu.be/VIDEO_ID
  https://youtube.com/watch?v=VIDEO_ID&t=30s   (extra query params stripped)
  https://www.youtube.com/embed/VIDEO_ID
  https://www.youtube.com/shorts/VIDEO_ID
  https://m.youtube.com/watch?v=VIDEO_ID

Canonical output
----------------
  https://www.youtube.com/watch?v=VIDEO_ID
"""

import logging
import re
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

# Matches paths like  /shorts/<id>  /embed/<id>  /v/<id>
_PATH_VIDEO_ID_RE = re.compile(r"^/(?:shorts|embed|v|e)/([A-Za-z0-9_-]{11})")

# Matches  youtu.be/<id>
_YOUTU_BE_RE = re.compile(r"^([A-Za-z0-9_-]{11})")

# Valid YouTube video IDs are exactly 11 URL-safe base64 characters
_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def extract_video_id(url: str) -> str | None:
    """
    Extract the 11-character YouTube video ID from *url*.

    Returns ``None`` if the URL does not look like a YouTube video URL
    or no valid ID can be found.
    """
    try:
        parsed = urlparse(url.strip())
    except Exception:
        return None

    hostname = parsed.hostname or ""
    hostname = hostname.removeprefix("www.").removeprefix("m.")

    # youtu.be short links

    if hostname == "youtu.be":
        # Path is  /<VIDEO_ID>
        path_segment = parsed.path.lstrip("/")
        m = _YOUTU_BE_RE.match(path_segment)
        if m and _VIDEO_ID_RE.match(m.group(1)):
            return m.group(1)

    # youtube.com variants

    if hostname in ("youtube.com", "youtube-nocookie.com"):
        # /shorts/<id>  /embed/<id>  /v/<id>  /e/<id>
        m = _PATH_VIDEO_ID_RE.match(parsed.path)
        if m and _VIDEO_ID_RE.match(m.group(1)):
            return m.group(1)

        # Standard watch URL: ?v=<id>
        qs = parse_qs(parsed.query)
        video_ids = qs.get("v", [])
        if video_ids and _VIDEO_ID_RE.match(video_ids[0]):
            return video_ids[0]

    return None


def normalize_youtube_url(url: str) -> str:
    """
    Return the canonical ``https://www.youtube.com/watch?v=<id>`` form of
    *url*, or the original *url* stripped of whitespace if the video ID
    cannot be extracted (so the caller still has a usable string).
    """
    video_id = extract_video_id(url)
    if video_id:
        canonical = f"https://www.youtube.com/watch?v={video_id}"
        if canonical != url.strip():
            logger.debug("Normalised YouTube URL: %r -> %r", url.strip(), canonical)
        return canonical

    logger.warning("Could not extract video ID from URL %r — using URL as-is.", url)
    return url.strip()
