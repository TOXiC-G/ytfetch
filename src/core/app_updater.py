import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Optional, Callable
import requests
from packaging import version


CURRENT_VERSION = "1.0.5"
GITHUB_REPO = "TOXiC-G/ytfetch"


class AppUpdater:
    @staticmethod
    def get_current_version() -> str:
        return CURRENT_VERSION

    @classmethod
    def is_installed_app(cls) -> bool:
        """
        Check if running from an Inno Setup installed location
        (unins*.exe in parent directory or running in Program Files).
        """
        if not getattr(sys, "frozen", False):
            return False

        try:
            current_exe = Path(sys.executable).resolve()
            exe_dir = current_exe.parent

            # 1. Inno Setup creates uninstaller (unins000.exe) in the app directory
            if list(exe_dir.glob("unins*.exe")):
                return True

            # 2. Check standard Program Files directories
            prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            exe_str = str(current_exe).lower()
            if exe_str.startswith(prog_files.lower()) or exe_str.startswith(prog_files_x86.lower()):
                return True
        except Exception:
            pass

        return False

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

                download_url = ""
                portable_url = ""
                setup_url = ""
                for asset in data.get("assets", []):
                    name = asset.get("name", "").lower()
                    url = asset.get("browser_download_url", "")
                    if name.endswith(".exe"):
                        if "setup" in name or "installer" in name:
                            setup_url = url
                        elif "portable" in name:
                            portable_url = url
                        elif not download_url:
                            download_url = url

                # Choose appropriate asset based on install type
                if cls.is_installed_app():
                    # For installed app, setup is preferred so Inno Setup can update files cleanly with UAC elevation
                    download_url = setup_url or download_url or portable_url
                else:
                    # For portable app, portable is preferred for in-place replacement
                    download_url = portable_url or download_url or setup_url

                if tag:
                    try:
                        is_newer = version.parse(tag) > version.parse(CURRENT_VERSION)
                        return is_newer, tag, download_url, body
                    except Exception:
                        if tag != CURRENT_VERSION:
                            return True, tag, download_url, body
        except Exception:
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
        Downloads the new binary and schedules restart without flashing console windows or infinite loops.
        """
        if not download_url:
            return False, "No downloadable binary found in the latest release."

        try:
            temp_dir = Path(tempfile.gettempdir()) / "ytfetch_update"
            temp_dir.mkdir(parents=True, exist_ok=True)

            is_installer = ("setup" in download_url.lower() or "installer" in download_url.lower())
            filename = f"ytfetch-v{target_version}-setup.exe" if is_installer else f"ytfetch-v{target_version}-portable.exe"
            new_exe = temp_dir / filename

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

            # If running as compiled exe, launch updater PowerShell script
            if getattr(sys, "frozen", False):
                current_exe = Path(sys.executable).resolve()
                current_pid = os.getpid()
                ps_script = temp_dir / "update_runner.ps1"

                # PowerShell script handles both installer and portable replacements cleanly and silently
                # Escaping single quotes for PowerShell literal strings
                esc_new_exe = str(new_exe).replace("'", "''")
                esc_current_exe = str(current_exe).replace("'", "''")
                is_installer_flag = "$true" if is_installer else "$false"

                ps_content = f"""# ytfetch updater runner
$ErrorActionPreference = 'SilentlyContinue'
$targetPid = {current_pid}
$newExe = '{esc_new_exe}'
$currentExe = '{esc_current_exe}'
$isInstaller = {is_installer_flag}

# 1. Wait for parent process to exit (timeout 10s)
try {{
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
    if ($proc) {{
        $proc.WaitForExit(10000)
    }}
}} catch {{}}

if ($isInstaller) {{
    # Installed App: Run installer with elevation (UAC prompt)
    try {{
        $installProc = Start-Process -FilePath $newExe -ArgumentList "/SILENT /CLOSEAPPLICATIONS" -Verb RunAs -PassThru -Wait
        if (Test-Path $currentExe) {{
            Start-Process -FilePath $currentExe
        }}
    }} catch {{
        # If UAC declined or failed, relaunch original app
        if (Test-Path $currentExe) {{
            Start-Process -FilePath $currentExe
        }}
    }}
}} else {{
    # Portable App: Replace current executable in-place with bounded retries (max 15 attempts / ~4.5s)
    $replaced = $false
    for ($i = 0; $i -lt 15; $i++) {{
        try {{
            Move-Item -Path $newExe -Destination $currentExe -Force -ErrorAction Stop
            $replaced = $true
            break
        }} catch {{
            Start-Sleep -Milliseconds 300
        }}
    }}
    
    # If direct Move-Item failed (e.g. permission restriction), attempt with elevation
    if (-not $replaced) {{
        try {{
            $cmd = "Move-Item -Path '$newExe' -Destination '$currentExe' -Force"
            Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $cmd" -Verb RunAs -Wait
            if (Test-Path $currentExe) {{
                $replaced = $true
            }}
        }} catch {{}}
    }}
    
    # Relaunch application
    if (Test-Path $currentExe) {{
        Start-Process -FilePath $currentExe
    }}
}}
"""
                with open(ps_script, "w", encoding="utf-8") as pf:
                    pf.write(ps_content)

                # Locate PowerShell binary reliably
                pwsh = shutil.which("powershell")
                if not pwsh:
                    sys_root = os.environ.get("SystemRoot", "C:\\Windows")
                    pwsh = os.path.join(sys_root, "System32", "WindowsPowerShell", "v1.0", "powershell.exe")

                # Launch detached and completely hidden (NO window flashing)
                CREATE_NO_WINDOW = 0x08000000
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                flags = CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

                subprocess.Popen(
                    [
                        pwsh,
                        "-NoProfile",
                        "-WindowStyle", "Hidden",
                        "-ExecutionPolicy", "Bypass",
                        "-File", str(ps_script)
                    ],
                    creationflags=flags
                )
                return True, "RESTART_READY"
            else:
                # In development mode
                return True, f"Downloaded update to {new_exe}. In development mode, please run git pull or execute the new binary."

        except Exception as e:
            return False, f"Failed to perform update: {e}"
