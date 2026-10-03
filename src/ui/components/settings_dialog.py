import threading
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QSpinBox, QComboBox, QFileDialog, QFrame, QMessageBox, QProgressBar
)
from PySide6.QtCore import Signal, Qt

from ...core.config import AppConfig
from ...core.ffmpeg_mgr import FFmpegManager
from ...core.updater import EngineUpdater


class SettingsDialog(QDialog):
    theme_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ApexLoad - Settings")
        self.setFixedWidth(520)
        self.cfg = AppConfig.get_instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Title
        title_lbl = QLabel("Application Settings")
        title_lbl.setObjectName("HeaderTitle")
        layout.addWidget(title_lbl)

        # 1. Download Location
        loc_card = QFrame()
        loc_card.setObjectName("Card")
        loc_layout = QVBoxLayout(loc_card)
        loc_layout.setContentsMargins(12, 12, 12, 12)
        loc_layout.setSpacing(6)

        loc_title = QLabel("Default Download Directory")
        loc_title.setObjectName("SectionTitle")

        loc_row = QHBoxLayout()
        self.path_edit = QLineEdit(self.cfg.get("download_path", ""))
        self.path_edit.setReadOnly(True)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse_clicked)

        loc_row.addWidget(self.path_edit, 1)
        loc_row.addWidget(browse_btn)

        loc_layout.addWidget(loc_title)
        loc_layout.addLayout(loc_row)
        layout.addWidget(loc_card)

        # 2. Preferences
        pref_card = QFrame()
        pref_card.setObjectName("Card")
        pref_layout = QVBoxLayout(pref_card)
        pref_layout.setContentsMargins(12, 12, 12, 12)
        pref_layout.setSpacing(10)

        pref_title = QLabel("General Preferences")
        pref_title.setObjectName("SectionTitle")
        pref_layout.addWidget(pref_title)

        # Concurrent downloads
        conc_row = QHBoxLayout()
        conc_lbl = QLabel("Max Concurrent Downloads:")
        self.spin_concurrent = QSpinBox()
        self.spin_concurrent.setRange(1, 6)
        self.spin_concurrent.setValue(self.cfg.get("max_concurrent_downloads", 3))
        conc_row.addWidget(conc_lbl)
        conc_row.addStretch()
        conc_row.addWidget(self.spin_concurrent)
        pref_layout.addLayout(conc_row)

        # Clipboard auto-detect
        self.chk_clipboard = QCheckBox("Automatically detect YouTube links on Windows clipboard")
        self.chk_clipboard.setChecked(self.cfg.get("auto_detect_clipboard", True))
        pref_layout.addWidget(self.chk_clipboard)

        # Theme selection
        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Appearance Theme:")
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Dark", "Light"])
        curr_theme = self.cfg.get("theme", "dark").capitalize()
        self.combo_theme.setCurrentText(curr_theme)
        theme_row.addWidget(theme_lbl)
        theme_row.addStretch()
        theme_row.addWidget(self.combo_theme)
        pref_layout.addLayout(theme_row)

        layout.addWidget(pref_card)

        # 3. Binaries & Engines (FFmpeg & yt-dlp)
        bin_card = QFrame()
        bin_card.setObjectName("Card")
        bin_layout = QVBoxLayout(bin_card)
        bin_layout.setContentsMargins(12, 12, 12, 12)
        bin_layout.setSpacing(10)

        bin_title = QLabel("Engine & Binaries Status")
        bin_title.setObjectName("SectionTitle")
        bin_layout.addWidget(bin_title)

        # FFmpeg status
        ffmpeg_row = QHBoxLayout()
        ffmpeg_lbl = QLabel("FFmpeg Transcoder:")
        self.ffmpeg_status_badge = QLabel("Checking...")
        self.ffmpeg_status_badge.setObjectName("Badge")

        ffmpeg_row.addWidget(ffmpeg_lbl)
        ffmpeg_row.addStretch()
        ffmpeg_row.addWidget(self.ffmpeg_status_badge)
        bin_layout.addLayout(ffmpeg_row)

        # yt-dlp status
        ytdlp_row = QHBoxLayout()
        ytdlp_lbl = QLabel(f"yt-dlp Core (v{EngineUpdater.get_current_version()}):")
        self.btn_update_engine = QPushButton("Check for Updates")
        self.btn_update_engine.clicked.connect(self._on_update_engine_clicked)

        ytdlp_row.addWidget(ytdlp_lbl)
        ytdlp_row.addStretch()
        ytdlp_row.addWidget(self.btn_update_engine)
        bin_layout.addLayout(ytdlp_row)

        layout.addWidget(bin_card)

        # Bottom buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("PrimaryButton")
        btn_save.clicked.connect(self._on_save_clicked)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

        self._check_ffmpeg_status()

    def _check_ffmpeg_status(self):
        ffmpeg_path, _ = FFmpegManager.get_binaries()
        if ffmpeg_path:
            self.ffmpeg_status_badge.setText("✓ Detected & Ready")
            self.ffmpeg_status_badge.setObjectName("StatusSuccess")
            self.ffmpeg_status_badge.setStyleSheet("background-color: rgba(16, 185, 129, 0.15); color: #34d399;")
        else:
            self.ffmpeg_status_badge.setText("✕ Missing")
            self.ffmpeg_status_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #f87171;")

    def _on_browse_clicked(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.path_edit.text())
        if dir_path:
            self.path_edit.setText(dir_path)

    def _on_update_engine_clicked(self):
        self.btn_update_engine.setText("Checking...")
        self.btn_update_engine.setEnabled(False)

        def worker():
            avail, current, latest = EngineUpdater.check_for_update()
            if avail:
                success, msg = EngineUpdater.update_engine()
                text = f"Updated to v{latest}" if success else "Update failed"
            else:
                text = "Up to date"
            self.btn_update_engine.setText(text)
            self.btn_update_engine.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()

    def _on_save_clicked(self):
        self.cfg.set("download_path", self.path_edit.text().strip())
        self.cfg.set("max_concurrent_downloads", self.spin_concurrent.value())
        self.cfg.set("auto_detect_clipboard", self.chk_clipboard.isChecked())
        
        new_theme = self.combo_theme.currentText().lower()
        if new_theme != self.cfg.get("theme", "dark"):
            self.cfg.set("theme", new_theme)
            self.theme_changed.emit(new_theme)

        self.accept()
