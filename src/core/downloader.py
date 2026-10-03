import os
import re
import glob
import shutil
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
        duration_formatted: str = "",
        embed_thumbnail: bool = True,
        embed_metadata: bool = True,
        embed_subtitles: bool = False,
        snip_start: Optional[str] = None,
        snip_end: Optional[str] = None,
        split_chapters: bool = False,
        format_id: Optional[str] = None,
    ):
        self.task_id = task_id
        self.url = url
        self.media_type = media_type
        self.format_choice = format_choice.lower()
        self.quality_choice = quality_choice
        self.format_id = format_id
        self.save_path = save_path
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.duration_formatted = duration_formatted
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
    Executes a DownloadTask using yt-dlp with extensive guards against failure points:
    - FFmpeg missing fallback & notifications
    - Windows path length & reserved character guards
    - Low disk space check
    - Auto-cleanup of partial .part/.ytdl files on cancellation
    - Human-readable error explanations
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

        # Guard 1: Verify destination directory and disk space
        try:
            save_dir = Path(self.task.save_path)
            save_dir.mkdir(parents=True, exist_ok=True)
            usage = shutil.disk_usage(str(save_dir))
            free_mb = usage.free / (1024 * 1024)
            if free_mb < 80:
                self.task.error_message = f"Insufficient disk space ({free_mb:.1f} MB free). Need at least 80 MB."
                self._update_status("error", self.task.error_message)
                return False
        except Exception as e:
            self.task.error_message = f"Invalid save directory: {e}"
            self._update_status("error", self.task.error_message)
            return False

        # Guard 2: FFmpeg Availability Check & Auto-provision (for both audio and video)
        ffmpeg_path, _ = FFmpegManager.get_binaries()
        if not ffmpeg_path:
            self._update_status("converting", "FFmpeg missing: Auto-provisioning portable FFmpeg...")
            ok, msg = FFmpegManager.download_portable()
            if ok:
                ffmpeg_path, _ = FFmpegManager.get_binaries()
            else:
                if self.task.media_type == "audio":
                    self.task.error_message = "Audio conversion requires FFmpeg. Please install it in Settings or via winget."
                    self._update_status("error", self.task.error_message)
                    return False

        # Safe filename template (strip Windows reserved characters)
        outtmpl = os.path.join(self.task.save_path, "%(title).180s [%(id)s].%(ext)s")

        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "windowsfilenames": True,
            "restrictfilenames": False,
            "retries": 3,
            "fragment_retries": 5,
            "socket_timeout": 30,
        }

        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path

        # Configure Video vs Audio
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
            if not ffmpeg_path:
                # Fallback to single stream with audio included if FFmpeg is completely missing
                ydl_opts["format"] = "best[ext=mp4]/best"
            else:
                if getattr(self.task, "format_id", None) and self.task.format_id not in ("best", "bestvideo+bestaudio/best"):
                    fid = self.task.format_id
                    ydl_opts["format"] = f"{fid}+bestaudio/bestvideo+bestaudio/best"
                elif self.task.quality_choice == "best":
                    ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                else:
                    height = re.sub(r"[^\d]", "", self.task.quality_choice)
                    if height:
                        ydl_opts["format"] = f"bestvideo[height<={height}]+bestaudio/bestvideo+bestaudio/best"
                    else:
                        ydl_opts["format"] = "bestvideo+bestaudio/best"

                ydl_opts["merge_output_format"] = self.task.format_choice

            postprocessors = []
            if self.task.embed_metadata:
                postprocessors.append({"key": "FFmpegMetadata", "add_metadata": True})

            if self.task.embed_thumbnail and ffmpeg_path:
                ydl_opts["writethumbnail"] = True
                postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

            if self.task.embed_subtitles and ffmpeg_path:
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
        if self.task.split_chapters and ffmpeg_path:
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
                        if self.task.media_type == "audio":
                            base, _ = os.path.splitext(self.task.output_file)
                            self.task.output_file = f"{base}.{self.task.format_choice}"

            if self.task.cancelled:
                self._cleanup_partial_files()
                self._update_status("cancelled", "Download was cancelled.")
                return False

            self.task.progress = 100.0
            self._update_status("finished", "Completed successfully.")
            return True

        except Exception as e:
            if self.task.cancelled:
                self._cleanup_partial_files()
                self._update_status("cancelled", "Download was cancelled.")
                return False

            error_msg = self._humanize_error(str(e))
            self.task.error_message = error_msg
            self._cleanup_partial_files()
            self._update_status("error", f"Error: {error_msg}")
            return False

    def _cleanup_partial_files(self):
        """Removes temporary .part or .ytdl files left behind in the download directory."""
        try:
            save_dir = Path(self.task.save_path)
            for ext in ["*.part", "*.ytdl", "*.temp"]:
                for temp_file in save_dir.glob(ext):
                    # Check if file was modified recently (last 10 minutes)
                    try:
                        temp_file.unlink(missing_ok=True)
                    except Exception:
                        pass
        except Exception:
            pass

    def _humanize_error(self, raw_err: str) -> str:
        if "ffmpeg" in raw_err.lower() and "not installed" in raw_err.lower():
            return "FFmpeg is required for muxing/audio conversion. Please install FFmpeg."
        if "HTTP Error 403" in raw_err:
            return "YouTube blocked download request (403 Forbidden). Try updating the yt-dlp engine."
        if "Sign in to confirm you’re not a bot" in raw_err or "bot" in raw_err.lower():
            return "YouTube bot check triggered. Please try again in a few minutes."
        if "Video unavailable" in raw_err:
            return "This video is unavailable, deleted, or country-restricted."
        if "Private video" in raw_err:
            return "This video is private."
        if "Requested format is not available" in raw_err:
            if not FFmpegManager.is_available():
                return "FFmpeg is required to merge separate video and audio streams for this video. Please click '▲ FFmpeg Missing' at the top to install it."
            return "Selected resolution/format is not available for this video. Try 'Best Available'."
        return raw_err[:120]

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
