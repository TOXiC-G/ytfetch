import sys
import os
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.ui.main_window import MainWindow


def create_default_icon() -> QIcon:
    """
    Dynamically creates a high-res brand icon for ApexLoad if no .ico file is present.
    """
    pixmap = QPixmap(128, 128)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Background circle with gradient
    painter.setBrush(QColor("#e11d48"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(4, 4, 120, 120, 28, 28)

    # Inner subtle glow
    painter.setBrush(QColor("#ffffff"))
    font = QFont("Segoe UI", 56, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("#ffffff"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "⚡")
    painter.end()

    return QIcon(pixmap)


def main():
    # Windows Taskbar AppUserModelID
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "ApexLoad.YouTubeDownloader.Desktop.1.0"
            )
        except Exception:
            pass

    # High DPI setup
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("ApexLoad")
    app.setOrganizationName("ApexLoad")
    app.setApplicationVersion("1.0.0")

    # Set icon
    icon_path = Path(__file__).resolve().parent / "assets" / "apexload.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        app.setWindowIcon(create_default_icon())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
