import sys
import os
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Callable
import requests

from .config import AppConfig


class FFmpegManager:
    # Reliable static mirrors
    MIRRORS = [
        "https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    ]

    @classmethod
    def get_binaries(cls) -> Tuple[Optional[str], Optional[str]]:
        """
        Locates ffmpeg.exe and ffprobe.exe.
        Returns (ffmpeg_path, ffprobe_path) or (None, None)
        """
        cfg = AppConfig.get_instance()
        custom = cfg.get("custom_ffmpeg_path", "")
        if custom and Path(custom).exists():
            custom_path = Path(custom)
            if custom_path.is_file() and custom_path.name.lower().startswith("ffmpeg"):
                ffprobe_candidate = custom_path.parent / "ffprobe.exe"
                return str(custom_path), str(ffprobe_candidate) if ffprobe_candidate.exists() else None
            elif custom_path.is_dir():
                ffmpeg = custom_path / "ffmpeg.exe"
                ffprobe = custom_path / "ffprobe.exe"
                if ffmpeg.exists():
                    return str(ffmpeg), str(ffprobe) if ffprobe.exists() else None

        # 1. Application Directory / Bundled bin
        app_candidates = [
            Path(sys.executable).parent / "bin",
            Path(sys.executable).parent,
            Path(__file__).resolve().parent.parent.parent / "bin",
            Path(__file__).resolve().parent.parent.parent / "dist" / "bin",
        ]
        for app_dir in app_candidates:
            cand = app_dir / "ffmpeg.exe"
            if cand.exists() and cls._verify_binary(str(cand)):
                ffprobe_cand = app_dir / "ffprobe.exe"
                return str(cand), str(ffprobe_cand) if ffprobe_cand.exists() else None

        # 2. Local ytfetch AppData bin
        local_bin = cfg.app_dir / "bin"
        local_ffmpeg = local_bin / "ffmpeg.exe"
        local_ffprobe = local_bin / "ffprobe.exe"
        if local_ffmpeg.exists() and cls._verify_binary(str(local_ffmpeg)):
            return str(local_ffmpeg), str(local_ffprobe) if local_ffprobe.exists() else None

        # 2. System PATH
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if ffmpeg and cls._verify_binary(ffmpeg):
            return ffmpeg, ffprobe

        # 3. Check WinGet Packages directory (scoped to *FFmpeg* packages)
        winget_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        if winget_path.exists():
            for pkg in winget_path.glob("*FFmpeg*"):
                for exe in pkg.glob("**/ffmpeg.exe"):
                    if cls._verify_binary(str(exe)):
                        ffprobe_cand = exe.parent / "ffprobe.exe"
                        return str(exe), str(ffprobe_cand) if ffprobe_cand.exists() else None

        # 4. Check known standard install locations
        known_dirs = [
            Path("C:\\ffmpeg\\bin"),
            Path("C:\\ffmpeg"),
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "ffmpeg" / "bin",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "ffmpeg",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ffmpeg" / "bin",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "ffmpeg",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ffmpeg" / "bin",
            Path(os.environ.get("ChocolateyInstall", "C:\\ProgramData\\chocolatey")) / "bin",
        ]
        for kdir in known_dirs:
            exe = kdir / "ffmpeg.exe"
            if exe.exists() and cls._verify_binary(str(exe)):
                ffprobe_cand = kdir / "ffprobe.exe"
                return str(exe), str(ffprobe_cand) if ffprobe_cand.exists() else None

        return None, None

    @classmethod
    def _verify_binary(cls, path: str) -> bool:
        try:
            res = subprocess.run(
                [path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            return res.returncode == 0
        except Exception:
            return False

    @classmethod
    def is_available(cls) -> bool:
        ffmpeg, _ = cls.get_binaries()
        return ffmpeg is not None

    @classmethod
    def download_portable(cls, progress_callback: Optional[Callable[[int, str], None]] = None) -> Tuple[bool, str]:
        """
        Downloads portable ffmpeg zip and extracts ffmpeg.exe and ffprobe.exe into %APPDATA%/ytfetch/bin
        """
        cfg = AppConfig.get_instance()
        target_dir = cfg.app_dir / "bin"
        target_dir.mkdir(parents=True, exist_ok=True)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        last_error = ""
        for url in cls.MIRRORS:
            try:
                if progress_callback:
                    progress_callback(5, f"Connecting to mirror...")

                with tempfile.TemporaryDirectory() as tmpdir:
                    zip_path = Path(tmpdir) / "ffmpeg.zip"
                    resp = requests.get(url, stream=True, timeout=25, headers=headers)
                    resp.raise_for_status()

                    total_size = int(resp.headers.get("content-length", 0))
                    downloaded = 0

                    with open(zip_path, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=1024 * 128):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if progress_callback and total_size > 0:
                                    pct = min(90, 5 + int((downloaded / total_size) * 85))
                                    mb = downloaded / (1024 * 1024)
                                    total_mb = total_size / (1024 * 1024)
                                    progress_callback(pct, f"Downloading FFmpeg ({mb:.1f}/{total_mb:.1f} MB)...")

                    if progress_callback:
                        progress_callback(92, "Extracting binaries...")

                    with zipfile.ZipFile(zip_path, "r") as zip_ref:
                        for member in zip_ref.namelist():
                            basename = Path(member).name.lower()
                            if basename in ("ffmpeg.exe", "ffprobe.exe"):
                                target_file = target_dir / basename
                                with zip_ref.open(member) as src, open(target_file, "wb") as dst:
                                    shutil.copyfileobj(src, dst)

                ffmpeg_file = target_dir / "ffmpeg.exe"
                if ffmpeg_file.exists() and cls._verify_binary(str(ffmpeg_file)):
                    if progress_callback:
                        progress_callback(100, "FFmpeg installed successfully!")
                    return True, "FFmpeg installed and verified successfully!"
            except Exception as e:
                last_error = str(e)
                continue

        return False, f"Failed to download FFmpeg: {last_error}"
