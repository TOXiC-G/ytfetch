import math
from typing import Dict, Any, List, Optional
import yt_dlp

from .sanitizer import URLSanitizer
from .ffmpeg_mgr import FFmpegManager


class MediaMetadataExtractor:
    """
    Extracts rich metadata, available streams, and estimated sizes using yt-dlp.
    """

    @classmethod
    def get_ydl_base_opts(cls) -> Dict[str, Any]:
        ffmpeg_path, _ = FFmpegManager.get_binaries()
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ignoreerrors": False,
        }
        if ffmpeg_path:
            opts["ffmpeg_location"] = ffmpeg_path
        return opts

    @classmethod
    def extract_info(cls, url: str, is_playlist_flat: bool = False) -> Dict[str, Any]:
        clean_url = URLSanitizer.sanitize(url)
        opts = cls.get_ydl_base_opts()
        
        if is_playlist_flat:
            opts["extract_flat"] = "in_playlist"
            opts["playlistend"] = 100  # Cap initial preview for responsiveness

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(clean_url, download=False)
                return cls._process_info(info, clean_url)
        except Exception as e:
            raw = str(e)
            if "HTTP Error 403" in raw:
                raise RuntimeError("YouTube blocked metadata request (403 Forbidden). Try updating the yt-dlp engine in Settings.")
            elif "Private video" in raw:
                raise RuntimeError("This video is private and cannot be accessed.")
            elif "Video unavailable" in raw:
                raise RuntimeError("Video is unavailable or has been removed.")
            elif "Sign in to confirm" in raw:
                raise RuntimeError("YouTube anti-bot verification encountered. Please try again shortly.")
            elif "is not a valid URL" in raw or "Unsupported URL" in raw:
                raise RuntimeError("Invalid or unsupported URL. Please paste a valid YouTube video or playlist link.")
            raise RuntimeError(raw)

    @classmethod
    def _process_info(cls, info: Dict[str, Any], url: str) -> Dict[str, Any]:
        if not info:
            raise ValueError("No metadata could be extracted from this URL.")

        is_playlist = info.get("_type") == "playlist" or "entries" in info

        if is_playlist:
            raw_entries = info.get("entries") or []
            entries = []
            for idx, entry in enumerate(raw_entries, 1):
                if not entry:
                    continue
                entries.append({
                    "index": idx,
                    "id": entry.get("id", ""),
                    "title": entry.get("title", f"Track {idx}"),
                    "duration": entry.get("duration", 0),
                    "duration_formatted": cls.format_duration(entry.get("duration", 0)),
                    "uploader": entry.get("uploader") or entry.get("channel", "Unknown"),
                    "thumbnail": entry.get("thumbnail") or (entry.get("thumbnails", [{}])[-1].get("url") if entry.get("thumbnails") else ""),
                    "url": entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "selected": True
                })

            return {
                "type": "playlist",
                "title": info.get("title", "YouTube Playlist"),
                "uploader": info.get("uploader") or info.get("channel", "Unknown"),
                "entries_count": len(entries),
                "entries": entries,
                "thumbnail": entries[0]["thumbnail"] if entries else None,
                "original_url": url,
            }

        # Single Video / Audio
        duration = info.get("duration") or 0
        formats = info.get("formats", [])
        
        # Parse available video resolutions and audio streams
        video_qualities = cls._parse_video_qualities(formats, duration)
        audio_qualities = cls._parse_audio_qualities(formats, duration)
        chapters = cls._parse_chapters(info.get("chapters") or [])

        # Thumbnails
        thumbnails = info.get("thumbnails") or []
        thumbnail_url = info.get("thumbnail")
        if not thumbnail_url and thumbnails:
            thumbnail_url = thumbnails[-1].get("url")

        return {
            "type": "video",
            "id": info.get("id"),
            "title": info.get("title", "Untitled"),
            "uploader": info.get("uploader") or info.get("channel", "Unknown"),
            "channel_url": info.get("channel_url"),
            "duration": duration,
            "duration_formatted": cls.format_duration(duration),
            "view_count": info.get("view_count", 0),
            "view_count_formatted": cls.format_views(info.get("view_count", 0)),
            "upload_date": info.get("upload_date"),
            "description": info.get("description", ""),
            "thumbnail": thumbnail_url,
            "video_qualities": video_qualities,
            "audio_qualities": audio_qualities,
            "chapters": chapters,
            "original_url": url,
        }

    @classmethod
    def _parse_video_qualities(cls, formats: List[Dict[str, Any]], duration: int) -> List[Dict[str, Any]]:
        # Map target heights
        height_map = {}
        for f in formats:
            height = f.get("height")
            vcodec = f.get("vcodec", "none")
            if not height or vcodec == "none":
                continue
            
            fps = f.get("fps") or 30
            filesize = f.get("filesize") or f.get("filesize_approx")
            vbr = f.get("vbr") or 0
            tbr = f.get("tbr") or 0

            # Estimate size if not available
            if not filesize and duration > 0 and (tbr > 0 or vbr > 0):
                bitrate_kbps = tbr if tbr > 0 else (vbr + 128)
                filesize = int((bitrate_kbps * 1000 / 8) * duration)

            if height not in height_map or (filesize and filesize > (height_map[height].get("filesize") or 0)):
                height_map[height] = {
                    "height": height,
                    "label": f"{height}p" + (f" {fps}fps" if fps and fps >= 50 else ""),
                    "fps": fps,
                    "format_id": f.get("format_id"),
                    "filesize": filesize,
                    "filesize_formatted": cls.format_size(filesize) if filesize else "Unknown size",
                    "ext": f.get("ext", "mp4")
                }

        # Sort descending by resolution
        sorted_qualities = sorted(height_map.values(), key=lambda x: x["height"], reverse=True)
        # Add "Best Available" at top
        best_size = sorted_qualities[0]["filesize"] if sorted_qualities else None
        res = [{
            "height": 9999,
            "label": "Best Available",
            "fps": 60,
            "format_id": "bestvideo+bestaudio/best",
            "filesize": best_size,
            "filesize_formatted": cls.format_size(best_size) if best_size else "Auto (~Best)",
            "ext": "mp4"
        }]
        res.extend(sorted_qualities)
        return res

    @classmethod
    def _parse_audio_qualities(cls, formats: List[Dict[str, Any]], duration: int) -> List[Dict[str, Any]]:
        # Common desired bitrates
        bitrates = [
            ("320 kbps (High Quality)", "320k", 320),
            ("256 kbps (Medium-High)", "256k", 256),
            ("192 kbps (Standard)", "192k", 192),
            ("128 kbps (Compact)", "128k", 128),
        ]
        res = []
        for label, code, kbps in bitrates:
            est_size = int((kbps * 1000 / 8) * duration) if duration > 0 else None
            res.append({
                "label": label,
                "bitrate": code,
                "kbps": kbps,
                "filesize": est_size,
                "filesize_formatted": cls.format_size(est_size) if est_size else "Variable"
            })
        return res

    @classmethod
    def _parse_chapters(cls, raw_chapters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chapters = []
        for ch in raw_chapters:
            start = ch.get("start_time", 0)
            end = ch.get("end_time", 0)
            title = ch.get("title", f"Chapter {len(chapters) + 1}")
            chapters.append({
                "title": title,
                "start_time": start,
                "end_time": end,
                "duration": end - start,
                "start_formatted": cls.format_duration(start),
                "end_formatted": cls.format_duration(end),
            })
        return chapters

    @staticmethod
    def format_duration(seconds: float) -> str:
        if not seconds:
            return "00:00"
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_size(bytes_num: Optional[int]) -> str:
        if not bytes_num or bytes_num <= 0:
            return "Unknown"
        units = ["B", "KB", "MB", "GB", "TB"]
        idx = 0
        size = float(bytes_num)
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024
            idx += 1
        return f"{size:.1f} {units[idx]}"

    @staticmethod
    def format_views(views: int) -> str:
        if not views:
            return "0 views"
        if views >= 1_000_000_000:
            return f"{views / 1_000_000_000:.1f}B views"
        if views >= 1_000_000:
            return f"{views / 1_000_000:.1f}M views"
        if views >= 1_000:
            return f"{views / 1_000:.1f}K views"
        return f"{views} views"
