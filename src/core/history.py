import os
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import AppConfig


class HistoryManager:
    _instance = None

    def __init__(self):
        cfg = AppConfig.get_instance()
        self.db_path = cfg.app_dir / "history.db"
        self._init_db()

    @classmethod
    def get_instance(cls) -> "HistoryManager":
        if cls._instance is None:
            cls._instance = HistoryManager()
        return cls._instance

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    format TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    thumbnail_url TEXT,
                    duration TEXT,
                    created_at REAL NOT NULL
                )
            """)
            conn.commit()

    def add_entry(
        self,
        title: str,
        url: str,
        media_type: str,
        format_choice: str,
        file_path: str,
        thumbnail_url: str = "",
        duration: str = "",
        file_size: int = 0
    ) -> int:
        if not file_size and os.path.exists(file_path):
            file_size = os.path.getsize(file_path)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO download_history (
                    title, url, media_type, format, file_path, file_size, thumbnail_url, duration, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title, url, media_type, format_choice, file_path, file_size, thumbnail_url, duration, time.time()
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all(self, limit: int = 150) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM download_history ORDER BY created_at DESC LIMIT ?", (limit,)
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                d = dict(r)
                d["exists"] = os.path.exists(d["file_path"])
                results.append(d)
            return results

    def delete_entry(self, entry_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM download_history WHERE id = ?", (entry_id,))
            conn.commit()

    def clear_all(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM download_history")
            conn.commit()

    @staticmethod
    def open_file(file_path: str) -> bool:
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)
                return True
            except Exception as e:
                print(f"Error opening file: {e}")
        return False

    @staticmethod
    def open_folder(file_path: str) -> bool:
        if os.path.exists(file_path):
            try:
                subprocess.Popen(f'explorer /select,"{os.path.abspath(file_path)}"')
                return True
            except Exception:
                pass
        parent = os.path.dirname(file_path)
        if os.path.exists(parent):
            try:
                subprocess.Popen(f'explorer "{os.path.abspath(parent)}"')
                return True
            except Exception:
                pass
        return False
