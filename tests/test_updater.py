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

    def test_is_installed_app(self):
        # In non-frozen test runner environment, is_installed_app should be False
        self.assertFalse(AppUpdater.is_installed_app())

    def test_current_version_matches(self):
        self.assertEqual(AppUpdater.get_current_version(), "1.0.5")


if __name__ == "__main__":
    unittest.main()
