import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import Tuple, Optional


class URLSanitizer:
    TRACKING_PARAMS = {
        "si", "feature", "ab_channel", "attribution_link", "fbclid",
        "gclid", "utm_source", "utm_medium", "utm_campaign", "utm_term",
        "utm_content", "spm"
    }

    YOUTUBE_DOMAINS = {
        "youtube.com", "www.youtube.com", "m.youtube.com",
        "music.youtube.com", "youtu.be"
    }

    @classmethod
    def is_youtube_url(cls, url: str) -> bool:
        if not url:
            return False
        try:
            parsed = urlparse(url.strip())
            netloc = parsed.netloc.lower()
            return any(netloc == domain or netloc.endswith("." + domain) for domain in cls.YOUTUBE_DOMAINS)
        except Exception:
            return False

    @classmethod
    def sanitize(cls, url: str) -> str:
        """
        Removes telemetry/tracking parameters while keeping video ID, playlist ID, timestamp etc.
        """
        if not url:
            return ""
        url = url.strip()
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = "https://" + url
                parsed = urlparse(url)

            query_dict = parse_qs(parsed.query)
            # Remove tracking params
            filtered_query = {
                k: v for k, v in query_dict.items() if k.lower() not in cls.TRACKING_PARAMS
            }

            clean_query = urlencode(filtered_query, doseq=True)
            sanitized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                clean_query,
                parsed.fragment
            ))
            return sanitized
        except Exception:
            return url

    @classmethod
    def detect_type(cls, url: str) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Returns (type, video_id, playlist_id)
        type can be: 'playlist', 'shorts', 'video', 'livestream', 'unknown'
        """
        clean_url = cls.sanitize(url)
        parsed = urlparse(clean_url)
        query = parse_qs(parsed.query)

        playlist_id = query.get("list", [None])[0]
        video_id = query.get("v", [None])[0]

        # Check for youtu.be shortlinks
        if "youtu.be" in parsed.netloc:
            parts = [p for p in parsed.path.split("/") if p]
            if parts:
                video_id = parts[0]

        # Check for /shorts/
        if "/shorts/" in parsed.path:
            parts = [p for p in parsed.path.split("/shorts/") if p]
            if parts:
                video_id = parts[-1].split("/")[0]
                return "shorts", video_id, playlist_id

        # Check for /live/
        if "/live/" in parsed.path:
            parts = [p for p in parsed.path.split("/live/") if p]
            if parts:
                video_id = parts[-1].split("/")[0]
                return "livestream", video_id, playlist_id

        if playlist_id and not video_id:
            return "playlist", None, playlist_id
        elif playlist_id and video_id:
            return "playlist_video", video_id, playlist_id
        elif video_id:
            return "video", video_id, None

        if cls.is_youtube_url(clean_url):
            return "video", None, None

        return "unknown", None, None
