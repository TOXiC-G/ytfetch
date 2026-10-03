from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Signal, Qt, QTimer
from PySide6.QtGui import QClipboard, QGuiApplication

from ...core.sanitizer import URLSanitizer
from ...core.config import AppConfig


class URLInputBar(QWidget):
    fetch_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_clipboard_url = ""
        self._setup_ui()
        self._setup_clipboard_watcher()

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(6)

        # Clipboard Detection Banner (initially hidden)
        self.banner = QFrame()
        self.banner.setObjectName("Banner")
        self.banner.setVisible(False)
        banner_layout = QHBoxLayout(self.banner)
        banner_layout.setContentsMargins(10, 6, 10, 6)
        banner_layout.setSpacing(8)

        self.banner_icon = QLabel("📋")
        self.banner_text = QLabel("Detected YouTube link on clipboard")
        self.banner_text.setObjectName("MutedLabel")
        self.banner_text.setStyleSheet("font-weight: 500;")

        self.banner_paste_btn = QPushButton("Paste & Fetch")
        self.banner_paste_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c3aed;
                color: white;
                font-weight: 600;
                font-size: 11px;
                padding: 4px 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        self.banner_paste_btn.clicked.connect(self._on_banner_paste_clicked)

        self.banner_dismiss_btn = QPushButton("✕")
        self.banner_dismiss_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                font-size: 12px;
                border: none;
                padding: 2px 6px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        self.banner_dismiss_btn.clicked.connect(lambda: self.banner.setVisible(False))

        banner_layout.addWidget(self.banner_icon)
        banner_layout.addWidget(self.banner_text, 1)
        banner_layout.addWidget(self.banner_paste_btn)
        banner_layout.addWidget(self.banner_dismiss_btn)

        self.main_layout.addWidget(self.banner)

        # URL Input Bar
        input_container = QHBoxLayout()
        input_container.setSpacing(8)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Paste YouTube video, shorts, or playlist URL here...")
        self.url_edit.setClearButtonEnabled(True)
        self.url_edit.returnPressed.connect(self._on_fetch_clicked)

        self.paste_btn = QPushButton("📋 Paste")
        self.paste_btn.clicked.connect(self._on_paste_btn_clicked)

        self.fetch_btn = QPushButton("Fetch Info")
        self.fetch_btn.setObjectName("PrimaryButton")
        self.fetch_btn.setMinimumWidth(110)
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)

        input_container.addWidget(self.url_edit, 1)
        input_container.addWidget(self.paste_btn)
        input_container.addWidget(self.fetch_btn)

        self.main_layout.addLayout(input_container)

    def _setup_clipboard_watcher(self):
        self.clipboard = QGuiApplication.clipboard()
        self.clipboard.dataChanged.connect(self.check_clipboard)
        
        # Periodic check timer for when user refocuses app
        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(2000)
        self.poll_timer.timeout.connect(self.check_clipboard)
        self.poll_timer.start()

    def check_clipboard(self):
        try:
            cfg = AppConfig.get_instance()
            if not cfg.get("auto_detect_clipboard", True):
                return

            text = self.clipboard.text().strip()
            if not text or text == self.last_clipboard_url:
                return

            if URLSanitizer.is_youtube_url(text):
                if text != self.url_edit.text().strip():
                    self.last_clipboard_url = text
                    # Shorten display link for banner
                    display_link = text if len(text) <= 50 else text[:47] + "..."
                    self.banner_text.setText(f"YouTube link detected: {display_link}")
                    self.banner.setVisible(True)
        except Exception:
            pass

    def _on_banner_paste_clicked(self):
        if self.last_clipboard_url:
            self.url_edit.setText(self.last_clipboard_url)
            self.banner.setVisible(False)
            self._on_fetch_clicked()

    def _on_paste_btn_clicked(self):
        text = self.clipboard.text().strip()
        if text:
            self.url_edit.setText(text)
            self.banner.setVisible(False)
            if URLSanitizer.is_youtube_url(text):
                self._on_fetch_clicked()

    def _on_fetch_clicked(self):
        url = self.url_edit.text().strip()
        if url:
            self.fetch_requested.emit(url)

    def set_loading(self, loading: bool):
        if loading:
            self.fetch_btn.setText("Fetching...")
            self.fetch_btn.setEnabled(False)
            self.url_edit.setEnabled(False)
        else:
            self.fetch_btn.setText("Fetch Info")
            self.fetch_btn.setEnabled(True)
            self.url_edit.setEnabled(True)
