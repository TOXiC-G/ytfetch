import sys
import subprocess
import requests
import yt_dlp
from typing import Tuple


class EngineUpdater:
    @staticmethod
    def get_current_version() -> str:
        return yt_dlp.version.__version__

    @staticmethod
    def check_for_update() -> Tuple[bool, str, str]:
        """
        Returns (update_available, current_version, latest_version)
        """
        current = yt_dlp.version.__version__
        try:
            resp = requests.get("https://pypi.org/pypi/yt-dlp/json", timeout=5)
            if resp.status_code == 200:
                latest = resp.json()["info"]["version"]
                return (latest != current), current, latest
        except Exception as e:
            print(f"Failed to check for updates: {e}")
        return False, current, current

    @staticmethod
    def update_engine() -> Tuple[bool, str]:
        """
        Runs pip install --upgrade yt-dlp in the active python environment.
        """
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if res.returncode == 0:
                return True, "yt-dlp successfully updated!"
            else:
                return False, f"Update failed: {res.stderr}"
        except Exception as e:
            return False, f"Exception during update: {e}"
