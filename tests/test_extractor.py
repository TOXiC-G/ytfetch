import unittest
from src.core.extractor import MediaMetadataExtractor


class TestExtractor(unittest.TestCase):
    def test_widescreen_and_standard_tiers(self):
        # 1920x1012 cinematic trailer should map to 1080p tier
        tier, label = MediaMetadataExtractor.get_resolution_tier(1920, 1012)
        self.assertEqual(tier, 1080)
        self.assertIn("1080p", label)

        # 1280x676 widescreen trailer should map to 720p tier
        tier, label = MediaMetadataExtractor.get_resolution_tier(1280, 676)
        self.assertEqual(tier, 720)
        self.assertIn("720p", label)

        # Standard 16:9 1080p
        tier, label = MediaMetadataExtractor.get_resolution_tier(1920, 1080)
        self.assertEqual(tier, 1080)

        # 4K widescreen
        tier, label = MediaMetadataExtractor.get_resolution_tier(3840, 2026)
        self.assertEqual(tier, 2160)
        self.assertIn("4K", label)

        # Vertical short (1080x1920)
        tier, label = MediaMetadataExtractor.get_resolution_tier(1080, 1920)
        self.assertEqual(tier, 1080)


if __name__ == "__main__":
    unittest.main()
