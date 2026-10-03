import os
import shutil
import subprocess
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Tuple
import requests

from .config import AppConfig


class FFmpegManager:
    GYAN_ESSENTIALS_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

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

        # 1. System PATH
        ffmpeg = shutil.which("ffmpeg")
        ffprobe = shutil.which("ffprobe")
        if ffmpeg and cls._verify_binary(ffmpeg):
            return ffmpeg, ffprobe

        # 2. Local AppData bin
        local_bin = cfg.app_dir / "bin"
        local_ffmpeg = local_bin / "ffmpeg.exe"
        local_ffprobe = local_bin / "ffprobe.exe"
        if local_ffmpeg.exists() and cls._verify_binary(str(local_ffmpeg)):
            return str(local_ffmpeg), str(local_ffprobe) if local_ffprobe.exists() else None

        # 3. Check WinGet Packages directory
        winget_path = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        if winget_path.exists():
            for exe in winget_path.glob("**/ffmpeg.exe"):
                if cls._verify_binary(str(exe)):
                    ffprobe_cand = exe.parent / "ffprobe.exe"
                    return str(exe), str(ffprobe_cand) if ffprobe_cand.exists() else None

        # 4. Check Program Files / common places
        for base in [os.environ.get("ProgramFiles", "C:\\Program Files"), os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]:
            if not base:
                continue
            for cand in Path(base).glob("**/ffmpeg.exe"):
                if cls._verify_binary(str(cand)):
                    ffprobe_cand = cand.parent / "ffprobe.exe"
                    return str(cand), str(ffprobe_cand) if ffprobe_cand.exists() else None

        return None, None

    @classmethod
    def _verify_binary(cls, path: str) -> bool:
        try:
            res = subprocess.run([path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            return res.returncode == 0
        except Exception:
            return False

    @classmethod
    def is_available(cls) -> bool:
        ffmpeg, _ = cls.get_binaries()
        return ffmpeg is not None

    @classmethod
    def download_portable(cls, progress_callback=None) -> bool:
        """
        Downloads portable ffmpeg essentials zip and extracts ffmpeg.exe and ffprobe.exe into %APPDATA%/ApexLoad/bin
        """
        cfg = AppConfig.get_instance()
        target_dir = cfg.app_dir / "bin"
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                zip_path = Path(tmpdir) / "ffmpeg.zip"
                response = requests.get(cls.GYAN_ESSENTIALS_URL, stream=True, timeout=30)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 64):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size > 0:
                                progress_callback(int((downloaded / total_size) * 100))

                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    for member in zip_ref.namelist():
                        basename = Path(member).name.lower()
                        if basename in ("ffmpeg.exe", "ffprobe.exe"):
                            source = zip_ref.open(member)
                            target = open(target_dir / basename, "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)

            return (target_dir / "ffmpeg.exe").exists()
        except Exception as e:
            print(f"Error downloading ffmpeg: {e}")
            return False
