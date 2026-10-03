import unittest
from src.core.app_updater import AppUpdater, CURRENT_VERSION


class TestAppUpdater(unittest.TestCase):
    def test_version_format(self):
        from packaging import version
        parsed = version.parse(CURRENT_VERSION)
        self.assertGreaterEqual(parsed.major, 1)

    def test_check_for_update_structure(self):
        # Should return a tuple of 4 elements without raising unhandled exceptions
        res = AppUpdater.check_for_app_update()
        self.assertEqual(len(res), 4)
        is_newer, tag, url, body = res
        self.assertIsInstance(is_newer, bool)
        self.assertIsInstance(tag, str)


if __name__ == "__main__":
    unittest.main()
