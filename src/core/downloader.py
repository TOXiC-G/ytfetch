import os
import re
import threading
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import yt_dlp

from .config import AppConfig
from .ffmpeg_mgr import FFmpegManager
from .sanitizer import URLSanitizer


class DownloadTask:
    def __init__(
        self,
        task_id: str,
        url: str,
        media_type: str,  # 'video' or 'audio'
        format_choice: str,  # 'mp4', 'mkv', 'webm', 'mp3', 'm4a', 'flac', 'wav', 'ogg'
        quality_choice: str,  # 'best', '1080', '720', etc. or bitrate '320k', '256k'
        save_path: str,
        title: str = "Media",
        thumbnail_url: str = "",
        embed_thumbnail: bool = True,
        embed_metadata: bool = True,
        embed_subtitles: bool = False,
        snip_start: Optional[str] = None,
        snip_end: Optional[str] = None,
        split_chapters: bool = False,
    ):
        self.task_id = task_id
        self.url = url
        self.media_type = media_type
        self.format_choice = format_choice.lower()
        self.quality_choice = quality_choice
        self.save_path = save_path
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.embed_thumbnail = embed_thumbnail
        self.embed_metadata = embed_metadata
        self.embed_subtitles = embed_subtitles
        self.snip_start = snip_start
        self.snip_end = snip_end
        self.split_chapters = split_chapters

        self.status = "queued"  # queued, downloading, converting, finished, error, cancelled
        self.progress = 0.0
        self.speed_str = "0 MB/s"
        self.eta_str = "--:--"
        self.size_str = "0 MB"
        self.error_message = ""
        self.output_file = ""
        self.cancelled = False

    def cancel(self):
        self.cancelled = True
        self.status = "cancelled"


class DownloadWorker:
    """
    Executes a DownloadTask using yt-dlp with callbacks and cancellation checks.
    """

    def __init__(
        self,
        task: DownloadTask,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        status_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.task = task
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self._ydl = None

    def run(self) -> bool:
        if self.task.cancelled:
            return False

        Path(self.task.save_path).mkdir(parents=True, exist_ok=True)
        ffmpeg_path, _ = FFmpegManager.get_binaries()

        # Sanitize safe filename template
        outtmpl = os.path.join(self.task.save_path, "%(title)s.%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "windowsfilenames": True,
            "restrictfilenames": False,
        }

        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path

        # Configure video vs audio
        if self.task.media_type == "audio":
            ydl_opts["format"] = "bestaudio/best"
            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.task.format_choice,
                    "preferredquality": self.task.quality_choice.replace("k", ""),
                }
            ]

            if self.task.embed_metadata:
                postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

            if self.task.embed_thumbnail and self.task.format_choice in ["mp3", "m4a", "flac"]:
                ydl_opts["writethumbnail"] = True
                postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            ydl_opts["postprocessors"] = postprocessors

        else:
            # Video configuration
            if self.task.quality_choice == "best":
                ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
            else:
                height = re.sub(r"[^\d]", "", self.task.quality_choice)
                if height:
                    ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
                else:
                    ydl_opts["format"] = "bestvideo+bestaudio/best"

            ydl_opts["merge_output_format"] = self.task.format_choice

            postprocessors = []
            if self.task.embed_metadata:
                postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

            if self.task.embed_thumbnail:
                ydl_opts["writethumbnail"] = True
                postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            if self.task.embed_subtitles:
                ydl_opts["writesubtitles"] = True
                ydl_opts["subtitleslangs"] = ["en", "all"]
                postprocessors.append({"key": "FFmpegEmbedSubtitle"})

            if postprocessors:
                ydl_opts["postprocessors"] = postprocessors

        # Snipping
        if self.task.snip_start or self.task.snip_end:
            start = self.task.snip_start or "00:00:00"
            end = self.task.snip_end
            if end:
                ydl_opts["download_ranges"] = yt_dlp.utils.download_range_func(
                    [], [(self._time_to_seconds(start), self._time_to_seconds(end))]
                )

        # Chapter splitting
        if self.task.split_chapters:
            ydl_opts["split_chapters"] = True

        self._update_status("downloading", "Starting download...")

        try:
            clean_url = URLSanitizer.sanitize(self.task.url)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._ydl = ydl
                info = ydl.extract_info(clean_url, download=True)
                
                # Retrieve final filename
                if info:
                    if "requested_downloads" in info and info["requested_downloads"]:
                        self.task.output_file = info["requested_downloads"][0].get("filepath", "")
                    if not self.task.output_file:
                        self.task.output_file = ydl.prepare_filename(info)
                        # adjust extension if converted
                        if self.task.media_type == "audio":
                            base, _ = os.path.splitext(self.task.output_file)
                            self.task.output_file = f"{base}.{self.task.format_choice}"

            if self.task.cancelled:
                self._update_status("cancelled", "Download was cancelled.")
                return False

            self.task.progress = 100.0
            self._update_status("finished", "Completed successfully.")
            return True

        except Exception as e:
            if self.task.cancelled:
                self._update_status("cancelled", "Download was cancelled.")
                return False
            error_msg = str(e)
            self.task.error_message = error_msg
            self._update_status("error", f"Error: {error_msg}")
            return False

    def _progress_hook(self, d: Dict[str, Any]):
        if self.task.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")

        status = d.get("status")
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            speed = d.get("speed") or 0
            eta = d.get("eta") or 0

            percent = (downloaded / total * 100.0) if total > 0 else 0.0
            self.task.progress = min(max(percent, 0.0), 99.0)

            # Speed
            if speed > 0:
                self.task.speed_str = f"{speed / (1024 * 1024):.2f} MB/s"
            else:
                self.task.speed_str = "-- MB/s"

            # ETA
            if eta > 0:
                m, s = divmod(int(eta), 60)
                h, m = divmod(m, 60)
                self.task.eta_str = f"{h:d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
            else:
                self.task.eta_str = "--:--"

            # Size
            if total > 0:
                self.task.size_str = f"{downloaded / (1024 * 1024):.1f} / {total / (1024 * 1024):.1f} MB"

            if self.progress_callback:
                self.progress_callback({
                    "task_id": self.task.task_id,
                    "progress": self.task.progress,
                    "speed": self.task.speed_str,
                    "eta": self.task.eta_str,
                    "size": self.task.size_str,
                    "status": "downloading"
                })

        elif status == "finished":
            self.task.progress = 99.0
            self._update_status("converting", "Converting & muxing...")

    def _postprocessor_hook(self, d: Dict[str, Any]):
        if self.task.cancelled:
            raise yt_dlp.utils.DownloadCancelled("Download cancelled by user.")
        
        status = d.get("status")
        if status == "started":
            self._update_status("converting", "Applying post-processing & metadata...")

    def _update_status(self, status: str, message: str):
        self.task.status = status
        if self.status_callback:
            self.status_callback(self.task.task_id, status)

    @staticmethod
    def _time_to_seconds(time_str: str) -> float:
        parts = time_str.strip().split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            return float(parts[0])
        except Exception:
            return 0.0
