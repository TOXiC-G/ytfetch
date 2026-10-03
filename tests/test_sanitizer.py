import unittest
from src.core.sanitizer import URLSanitizer


class TestURLSanitizer(unittest.TestCase):
    def test_strip_tracking(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&si=abcdef12345&feature=shared"
        sanitized = URLSanitizer.sanitize(url)
        self.assertIn("v=dQw4w9WgXcQ", sanitized)
        self.assertNotIn("si=", sanitized)
        self.assertNotIn("feature=", sanitized)

    def test_detect_type_video(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        media_type, vid, pid = URLSanitizer.detect_type(url)
        self.assertEqual(media_type, "video")
        self.assertEqual(vid, "dQw4w9WgXcQ")
        self.assertIsNone(pid)

    def test_detect_type_shorts(self):
        url = "https://www.youtube.com/shorts/3jz_eT_5cWk?si=abcdef"
        media_type, vid, pid = URLSanitizer.detect_type(url)
        self.assertEqual(media_type, "shorts")
        self.assertEqual(vid, "3jz_eT_5cWk")

    def test_detect_type_playlist(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOdP_8GztsuKi9zn5Q844009"
        media_type, vid, pid = URLSanitizer.detect_type(url)
        self.assertEqual(media_type, "playlist")
        self.assertIsNone(vid)
        self.assertEqual(pid, "PLrAXtmErZgOdP_8GztsuKi9zn5Q844009")

    def test_detect_youtu_be(self):
        url = "https://youtu.be/dQw4w9WgXcQ?t=42"
        media_type, vid, pid = URLSanitizer.detect_type(url)
        self.assertEqual(vid, "dQw4w9WgXcQ")


if __name__ == "__main__":
    unittest.main()
