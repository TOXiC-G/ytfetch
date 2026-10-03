import unittest
import os
import sys

# Run Qt offscreen for headless CI runners
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow


class TestUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_main_window_init(self):
        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertFalse(window.windowIcon().isNull(), "Window icon should be valid and loaded")
        self.assertIn("ytfetch", window.windowTitle())
        window.close()


if __name__ == "__main__":
    unittest.main()
