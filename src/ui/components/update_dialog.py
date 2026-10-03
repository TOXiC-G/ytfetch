import sys
import os
import threading
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QMessageBox, QApplication
)
from PySide6.QtCore import Qt, Signal, QObject

from ...core.app_updater import AppUpdater, CURRENT_VERSION


class UpdateSignals(QObject):
    progress = Signal(int, str)
    finished = Signal(bool, str)


class UpdateDialog(QDialog):
    def __init__(self, target_version: str, download_url: str, release_notes: str, parent=None):
        super().__init__(parent)
        self.target_version = target_version
        self.download_url = download_url
        self.release_notes = release_notes
        self.signals = UpdateSignals()
        self.signals.progress.connect(self._on_progress)
        self.signals.finished.connect(self._on_finished)

        self.setWindowTitle(f"ytfetch - Update Available (v{target_version})")
        self.setFixedWidth(460)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Title
        title = QLabel(f"✨ Version {self.target_version} is Available!")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        sub = QLabel(f"You are currently running ytfetch v{CURRENT_VERSION}.")
        sub.setObjectName("MutedLabel")
        layout.addWidget(sub)

        # Release Notes Label & Box
        rn_lbl = QLabel("What's New:")
        rn_lbl.setObjectName("SectionTitle")
        layout.addWidget(rn_lbl)

        self.notes_box = QTextEdit()
        self.notes_box.setReadOnly(True)
        self.notes_box.setPlainText(self.release_notes or "Bug fixes and performance improvements.")
        self.notes_box.setFixedHeight(120)
        self.notes_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(20, 24, 35, 0.4);
                border: 1px solid rgba(120, 130, 160, 0.2);
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.notes_box)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("MutedLabel")
        self.status_lbl.setVisible(False)
        layout.addWidget(self.status_lbl)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_later = QPushButton("Later")
        self.btn_later.clicked.connect(self.reject)

        self.btn_update = QPushButton("Update & Restart")
        self.btn_update.setObjectName("PrimaryButton")
        self.btn_update.clicked.connect(self._start_update)

        btn_row.addWidget(self.btn_later)
        btn_row.addWidget(self.btn_update)
        layout.addLayout(btn_row)

    def _start_update(self):
        if not self.download_url:
            QMessageBox.information(
                self,
                "No Binary Asset",
                f"Release v{self.target_version} was found on GitHub, but no executable asset has been uploaded to the release yet."
            )
            return

        self.btn_update.setEnabled(False)
        self.btn_later.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_lbl.setVisible(True)
        self.status_lbl.setText("Starting download...")

        def worker():
            def prog_cb(pct, text):
                self.signals.progress.emit(pct, text)

            ok, msg = AppUpdater.download_and_apply_update(
                self.download_url,
                self.target_version,
                progress_callback=prog_cb
            )
            self.signals.finished.emit(ok, msg)

        threading.Thread(target=worker, daemon=True).start()

    def _on_progress(self, pct: int, text: str):
        self.progress_bar.setValue(pct)
        self.status_lbl.setText(text)

    def _on_finished(self, ok: bool, msg: str):
        if ok:
            if msg == "RESTART_READY":
                self.status_lbl.setText("Restarting ytfetch...")
                QApplication.quit()
                os._exit(0)
            else:
                QMessageBox.information(self, "Update Downloaded", msg)
                self.accept()
        else:
            QMessageBox.critical(self, "Update Failed", msg)
            self.btn_update.setEnabled(True)
            self.btn_later.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_lbl.setVisible(False)
