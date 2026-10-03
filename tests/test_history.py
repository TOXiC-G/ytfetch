import unittest
import os
import tempfile
from pathlib import Path
from src.core.history import HistoryManager
from src.core.ffmpeg_mgr import FFmpegManager


class TestHistoryAndFFmpeg(unittest.TestCase):
    def test_ffmpeg_detection(self):
        ffmpeg, ffprobe = FFmpegManager.get_binaries()
        self.assertIsNotNone(ffmpeg, "FFmpeg should be detected on this system")
        self.assertTrue(os.path.exists(ffmpeg))

    def test_history_crud(self):
        history = HistoryManager.get_instance()
        initial_len = len(history.get_all())
        
        entry_id = history.add_entry(
            title="Test Song",
            url="https://www.youtube.com/watch?v=123",
            media_type="audio",
            format_choice="mp3",
            file_path="C:/dummy/path/test.mp3",
            file_size=1024
        )
        self.assertIsNotNone(entry_id)
        
        all_entries = history.get_all()
        self.assertGreaterEqual(len(all_entries), initial_len + 1)
        
        history.delete_entry(entry_id)
        self.assertEqual(len(history.get_all()), initial_len)


if __name__ == "__main__":
    unittest.main()
