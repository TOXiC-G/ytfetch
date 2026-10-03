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
from src.core.app_updater import CURRENT_VERSION


def create_default_icon() -> QIcon:
    """
    Dynamically creates a high-res brand icon for ytfetch if no .ico file is present.
    """
    pixmap = QPixmap(128, 128)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # YouTube red badge
    painter.setBrush(QColor("#FF0000"))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(8, 20, 112, 88, 24, 24)

    # Downward download arrow + dock bar
    painter.setBrush(QColor("#ffffff"))
    # Arrow shaft
    painter.drawRoundedRect(56, 36, 16, 26, 3, 3)
    # Arrow head
    from PySide6.QtGui import QPainterPath
    head = QPainterPath()
    head.moveTo(38, 58)
    head.lineTo(90, 58)
    head.lineTo(64, 82)
    head.closeSubpath()
    painter.fillPath(head, QColor("#ffffff"))
    # Dock bar
    painter.drawRoundedRect(42, 88, 44, 8, 3, 3)
    painter.end()

    return QIcon(pixmap)


def main():
    # Windows Taskbar AppUserModelID
    if sys.platform == "win32":
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f"TOXiC-G.ytfetch.Desktop.{CURRENT_VERSION}"
            )
        except Exception:
            pass

    # High DPI setup
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("ytfetch")
    app.setOrganizationName("TOXiC-G")
    app.setApplicationVersion(CURRENT_VERSION)

    # Set icon
    icon_path = Path(__file__).resolve().parent / "assets" / "ytfetch.ico"
    if not icon_path.exists():
        icon_path = Path(__file__).resolve().parent / "assets" / "ytfetch.png"

    if icon_path.exists():
        app_icon = QIcon(str(icon_path))
    else:
        app_icon = create_default_icon()

    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
