import sys
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Callable
import requests
from packaging import version


CURRENT_VERSION = "1.0.2"
GITHUB_REPO = "TOXiC-G/ytfetch"


class AppUpdater:
    @staticmethod
    def get_current_version() -> str:
        return CURRENT_VERSION

    @classmethod
    def check_for_app_update(cls) -> Tuple[bool, str, str, str]:
        """
        Non-invasive check against GitHub Releases API.
        Returns (update_available, latest_version, download_url, release_notes)
        """
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"ytfetch-desktop/{CURRENT_VERSION}"
        }

        try:
            resp = requests.get(api_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                tag = data.get("tag_name", "").lstrip("v")
                body = data.get("body", "No release notes provided.")

                # Look for executable asset: prefer portable for direct in-place update, otherwise setup
                download_url = ""
                portable_url = ""
                setup_url = ""
                for asset in data.get("assets", []):
                    name = asset.get("name", "").lower()
                    url = asset.get("browser_download_url", "")
                    if name.endswith(".exe"):
                        if "portable" in name:
                            portable_url = url
                        elif "setup" in name or "installer" in name:
                            setup_url = url
                        elif not download_url:
                            download_url = url

                download_url = portable_url or setup_url or download_url

                if tag:
                    try:
                        is_newer = version.parse(tag) > version.parse(CURRENT_VERSION)
                        return is_newer, tag, download_url, body
                    except Exception:
                        if tag != CURRENT_VERSION:
                            return True, tag, download_url, body
        except Exception as e:
            # Silent failure during background check
            pass

        return False, CURRENT_VERSION, "", ""

    @classmethod
    def download_and_apply_update(
        cls,
        download_url: str,
        target_version: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        Downloads the new executable and schedules restart.
        """
        if not download_url:
            return False, "No downloadable binary found in the latest release."

        try:
            temp_dir = Path(tempfile.gettempdir()) / "ytfetch_update"
            temp_dir.mkdir(parents=True, exist_ok=True)
            new_exe = temp_dir / f"ytfetch-{target_version}.exe"

            headers = {
                "User-Agent": f"ytfetch-desktop/{CURRENT_VERSION}"
            }
            resp = requests.get(download_url, stream=True, headers=headers, timeout=30)
            resp.raise_for_status()

            total_size = int(resp.headers.get("content-length", 0))
            downloaded = 0

            with open(new_exe, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            pct = int((downloaded / total_size) * 100)
                            mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            progress_callback(pct, f"Downloading v{target_version} ({mb:.1f}/{total_mb:.1f} MB)...")

            if not new_exe.exists() or new_exe.stat().st_size < 1000:
                return False, "Downloaded file appears incomplete or corrupt."

            # If running as compiled exe, launch updater batch script
            if getattr(sys, "frozen", False):
                current_exe = Path(sys.executable).resolve()
                bat_script = temp_dir / "update_restart.bat"
                
                # Script waits for current process to release the file lock, moves new exe over, launches it, and self-deletes
                bat_content = f"""@echo off
timeout /t 1 /nobreak >nul
:retry
move /y "{new_exe}" "{current_exe}" >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto retry
)
start "" "{current_exe}"
del "%~f0"
"""
                with open(bat_script, "w", encoding="utf-8") as bf:
                    bf.write(bat_content)

                # Launch detached batch
                subprocess.Popen(
                    ["cmd.exe", "/c", str(bat_script)],
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
                )
                return True, "RESTART_READY"
            else:
                # In python source / dev mode
                return True, f"Downloaded update to {new_exe}. In development mode, please run git pull or execute the new binary."

        except Exception as e:
            return False, f"Failed to perform update: {e}"
