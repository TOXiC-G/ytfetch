import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict


class AppConfig:
    _instance = None

    def __init__(self):
        appdata_base = Path(os.environ.get("APPDATA", Path.home()))
        self.app_dir = appdata_base / "ytfetch"
        old_dir = appdata_base / "ApexLoad"
        
        # Migrate old config/history if exists
        if old_dir.exists() and not self.app_dir.exists():
            try:
                shutil.copytree(old_dir, self.app_dir)
            except Exception:
                pass

        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.app_dir / "config.json"
        
        default_download = Path.home() / "Downloads" / "ytfetch"
        self.defaults: Dict[str, Any] = {
            "download_path": str(default_download),
            "theme": "dark",
            "max_concurrent_downloads": 3,
            "auto_detect_clipboard": True,
            "auto_check_updates": True,
            "default_media_type": "video",
            "default_video_quality": "best",
            "default_audio_format": "mp3",
            "default_audio_bitrate": "320k",
            "embed_thumbnail": True,
            "embed_metadata": True,
            "embed_subtitles": False,
            "custom_ffmpeg_path": ""
        }
        self.data = self.load()

    @classmethod
    def get_instance(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = AppConfig()
        return cls._instance

    def load(self) -> Dict[str, Any]:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cfg = self.defaults.copy()
                    cfg.update(saved)
                    return cfg
            except Exception:
                return self.defaults.copy()
        return self.defaults.copy()

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, self.defaults.get(key, default))

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.save()
