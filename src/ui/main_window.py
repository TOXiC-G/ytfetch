import uuid
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QMessageBox, QProgressDialog, QStackedWidget
)
from PySide6.QtCore import Qt, QRunnable, QThreadPool, Signal, QObject, QTimer
from PySide6.QtGui import QIcon

from ..core.config import AppConfig
from ..core.sanitizer import URLSanitizer
from ..core.extractor import MediaMetadataExtractor
from ..core.downloader import DownloadTask
from ..core.ffmpeg_mgr import FFmpegManager
from ..core.app_updater import AppUpdater, CURRENT_VERSION
from .theme import Theme
from .components import (
    URLInputBar, PreviewCard, OptionsPanel, PlaylistView,
    QueueWidget, HistoryWidget, SettingsDialog, UpdateDialog
)


class MetadataFetchSignals(QObject):
    success = Signal(dict)
    error = Signal(str)


class MetadataFetchRunnable(QRunnable):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.signals = MetadataFetchSignals()

    def run(self):
        try:
            info = MediaMetadataExtractor.extract_info(self.url)
            self.signals.success.emit(info)
        except Exception as e:
            self.signals.error.emit(str(e))


class MainWindow(QMainWindow):
    update_detected = Signal(str, str, str)  # target_version, download_url, notes

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"ytfetch - YouTube Downloader & Converter (v{CURRENT_VERSION})")
        self.resize(1000, 740)
        self.setMinimumSize(850, 620)

        self.cfg = AppConfig.get_instance()
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.thread_pool = QThreadPool.globalInstance()

        icon_path = Path(__file__).resolve().parent.parent / "assets" / "ytfetch.ico"
        if not icon_path.exists():
            icon_path = Path(__file__).resolve().parent.parent / "assets" / "ytfetch.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.update_detected.connect(self._on_update_detected)
        self.pending_update_data: Optional[Dict[str, str]] = None

        self._setup_ui()
        self._apply_theme(self.cfg.get("theme", "dark"))

        # Schedule non-invasive update check 2 seconds after startup
        if self.cfg.get("auto_check_updates", True):
            QTimer.singleShot(2000, self._check_for_updates_silently)

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(18, 14, 18, 14)
        root_layout.setSpacing(14)

        # 1. Header Bar (Clean, no emoji in title)
        header = QHBoxLayout()
        header.setSpacing(10)

        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(8)

        logo_title = QLabel("ytfetch")
        logo_title.setObjectName("HeaderTitle")

        logo_version = QLabel(f"v{CURRENT_VERSION}")
        logo_version.setObjectName("Badge")

        logo_layout.addWidget(logo_title)
        logo_layout.addWidget(logo_version)

        header.addLayout(logo_layout)
        header.addStretch()

        # Update Notice Button (Hidden by default, shown quietly if update found)
        self.btn_update_notice = QPushButton("✨ Update Available")
        self.btn_update_notice.setObjectName("UpdateNoticeButton")
        self.btn_update_notice.setVisible(False)
        self.btn_update_notice.clicked.connect(self._on_update_notice_clicked)
        header.addWidget(self.btn_update_notice)

        # Engine Status
        ffmpeg_avail = FFmpegManager.is_available()
        self.engine_status = QPushButton("● FFmpeg Ready" if ffmpeg_avail else "▲ FFmpeg Missing")
        self.engine_status.setObjectName("StatusSuccess" if ffmpeg_avail else "StatusError")
        self.engine_status.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 6px;
            }
        """)
        self.engine_status.clicked.connect(self._on_engine_status_clicked)

        # Theme toggle button
        self.btn_theme_toggle = QPushButton("🌙" if self.cfg.get("theme", "dark") == "dark" else "☀️")
        self.btn_theme_toggle.setObjectName("IconButton")
        self.btn_theme_toggle.setToolTip("Toggle Dark/Light Mode")
        self.btn_theme_toggle.clicked.connect(self._toggle_theme)

        # Settings button
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setObjectName("IconButton")
        self.btn_settings.setToolTip("Settings")
        self.btn_settings.clicked.connect(self._open_settings)

        header.addWidget(self.engine_status)
        header.addWidget(self.btn_theme_toggle)
        header.addWidget(self.btn_settings)

        root_layout.addLayout(header)

        # 2. URL Input Bar
        self.url_bar = URLInputBar()
        self.url_bar.fetch_requested.connect(self._on_fetch_requested)
        root_layout.addWidget(self.url_bar)

        # 3. Main Navigation Tabs (Downloader & History only)
        self.tabs = QTabWidget()

        # Tab 1: Downloader with QStackedWidget for smooth transition to Playlist Inspector
        self.downloader_stack = QStackedWidget()

        # Page 0: Downloader Hub
        hub_widget = QWidget()
        hub_layout = QVBoxLayout(hub_widget)
        hub_layout.setContentsMargins(8, 12, 8, 8)
        hub_layout.setSpacing(12)

        # Preview Card (contains the Inspect Playlist button on the right)
        self.preview_card = PreviewCard()
        self.preview_card.inspect_playlist_requested.connect(self._show_playlist_inspector)
        hub_layout.addWidget(self.preview_card)

        # Options Panel
        self.options_panel = OptionsPanel()
        self.options_panel.download_now_requested.connect(self._on_download_now)
        self.options_panel.add_queue_requested.connect(self._on_add_to_queue)
        self.options_panel.options_changed.connect(self.preview_card.update_estimated_size)
        hub_layout.addWidget(self.options_panel)

        # Active Queue Preview inside Downloader tab
        hub_layout.addWidget(QLabel("Current Downloads:"))
        self.queue_widget = QueueWidget()
        self.queue_widget.task_finished_signal.connect(self._on_task_finished)
        hub_layout.addWidget(self.queue_widget, 1)

        self.downloader_stack.addWidget(hub_widget)

        # Page 1: Playlist Inspector View (integrated into Downloader tab)
        self.playlist_view = PlaylistView()
        self.playlist_view.back_requested.connect(self._show_downloader_hub)
        self.playlist_view.selection_changed.connect(self._on_playlist_selection_changed)
        self.playlist_view.download_selected_requested.connect(self._on_playlist_download_selected)
        self.downloader_stack.addWidget(self.playlist_view)

        self.tabs.addTab(self.downloader_stack, "📥 Downloader")

        # Tab 2: History
        self.history_widget = HistoryWidget()
        self.tabs.addTab(self.history_widget, "🕒 History")

        root_layout.addWidget(self.tabs, 1)

        # 4. Footer Bar (Bottom Right Credit)
        footer = QHBoxLayout()
        footer.setContentsMargins(4, 2, 4, 0)
        footer.addStretch()

        self.lbl_credit = QLabel("By Nathan Latino Henriques")
        self.lbl_credit.setObjectName("FooterCredit")
        footer.addWidget(self.lbl_credit)

        root_layout.addLayout(footer)

    def _show_playlist_inspector(self):
        self.downloader_stack.setCurrentIndex(1)

    def _show_downloader_hub(self):
        self.downloader_stack.setCurrentIndex(0)

    def _on_playlist_selection_changed(self, selected_count: int, total_count: int):
        self.preview_card.update_selection_count(selected_count, total_count)
        self.options_panel.update_selected_count(selected_count)

    def _apply_theme(self, theme_name: str):
        stylesheet = Theme.get_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
        self.btn_theme_toggle.setText("🌙" if theme_name == "dark" else "☀️")

    def _toggle_theme(self):
        curr = self.cfg.get("theme", "dark")
        new_theme = "light" if curr == "dark" else "dark"
        self.cfg.set("theme", new_theme)
        self._apply_theme(new_theme)

    def _check_for_updates_silently(self):
        def worker():
            is_newer, tag, url, body = AppUpdater.check_for_app_update()
            if is_newer:
                self.update_detected.emit(tag, url, body)

        threading.Thread(target=worker, daemon=True).start()

    def _on_update_detected(self, target_version: str, download_url: str, notes: str):
        self.pending_update_data = {
            "version": target_version,
            "url": download_url,
            "notes": notes
        }
        self.btn_update_notice.setText(f"✨ Update v{target_version}")
        self.btn_update_notice.setVisible(True)

    def _on_update_notice_clicked(self):
        if self.pending_update_data:
            dlg = UpdateDialog(
                target_version=self.pending_update_data["version"],
                download_url=self.pending_update_data["url"],
                release_notes=self.pending_update_data["notes"],
                parent=self
            )
            dlg.exec()

    def _on_engine_status_clicked(self):
        if not FFmpegManager.is_available():
            reply = QMessageBox.question(
                self,
                "FFmpeg Missing",
                "FFmpeg is required to mux video/audio and extract MP3s.\n\nWould you like ytfetch to automatically download and configure portable FFmpeg now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._download_ffmpeg_interactive()
        else:
            self._open_settings()

    def _download_ffmpeg_interactive(self):
        progress = QProgressDialog("Downloading portable FFmpeg...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        def worker():
            def cb(pct, text):
                progress.setValue(pct)
                progress.setLabelText(text)

            ok, msg = FFmpegManager.download_portable(cb)
            progress.close()
            if ok:
                QMessageBox.information(self, "FFmpeg Installed", "FFmpeg has been installed and configured successfully!")
                self._update_engine_badge()
            else:
                QMessageBox.critical(self, "Download Failed", f"Could not install FFmpeg: {msg}")

        threading.Thread(target=worker, daemon=True).start()

    def _update_engine_badge(self):
        ffmpeg_avail = FFmpegManager.is_available()
        self.engine_status.setText("● FFmpeg Ready" if ffmpeg_avail else "▲ FFmpeg Missing")
        self.engine_status.setObjectName("StatusSuccess" if ffmpeg_avail else "StatusError")
        self.engine_status.setStyleSheet("")

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.theme_changed.connect(self._apply_theme)
        if dlg.exec():
            self._update_engine_badge()

    def _on_fetch_requested(self, url: str):
        self.url_bar.set_loading(True)
        runnable = MetadataFetchRunnable(url)
        runnable.signals.success.connect(self._on_metadata_success)
        runnable.signals.error.connect(self._on_metadata_error)
        self.thread_pool.start(runnable)

    def _on_metadata_success(self, data: Dict[str, Any]):
        self.url_bar.set_loading(False)
        self.current_metadata = data

        is_playlist = (data.get("type") == "playlist")

        # Update preview card & options panel
        self.preview_card.set_metadata(data)
        self.options_panel.set_metadata(data)

        if is_playlist:
            self.playlist_view.load_playlist(data)
            # Ensure we start on Downloader Hub showing the preview card with the Inspect button
            self.downloader_stack.setCurrentIndex(0)
            self.tabs.setCurrentIndex(0)
        else:
            self.downloader_stack.setCurrentIndex(0)
            self.tabs.setCurrentIndex(0)

    def _on_metadata_error(self, error_msg: str):
        self.url_bar.set_loading(False)
        QMessageBox.warning(
            self,
            "Failed to Fetch Information",
            f"Could not retrieve video or playlist information.\n\nDetails:\n{error_msg}"
        )

    def _on_download_now(self, options: Dict[str, Any]):
        self._queue_current_media(options, switch_to_queue=True)

    def _on_add_to_queue(self, options: Dict[str, Any]):
        self._queue_current_media(options, switch_to_queue=False)

    def _queue_current_media(self, options: Dict[str, Any], switch_to_queue: bool = False):
        if not self.current_metadata:
            QMessageBox.information(self, "No Video", "Please fetch a valid YouTube video or playlist first.")
            return

        # Check if playlist
        if self.current_metadata.get("type") == "playlist":
            selected = self.playlist_view.get_selected_entries()
            if not selected:
                QMessageBox.warning(self, "No Items Selected", "Please select at least one video to download.")
                return
            self._download_entries(selected, options)
            return

        # Single video
        task = DownloadTask(
            task_id=str(uuid.uuid4()),
            url=self.current_metadata.get("original_url") or "",
            media_type=options["media_type"],
            format_choice=options["format_choice"],
            quality_choice=options["quality_choice"],
            save_path=options["save_path"],
            title=self.current_metadata.get("title", "Video"),
            thumbnail_url=self.current_metadata.get("thumbnail", ""),
            duration_formatted=self.current_metadata.get("duration_formatted", ""),
            embed_thumbnail=options.get("embed_thumbnail", True),
            embed_metadata=options.get("embed_metadata", True),
            embed_subtitles=options.get("embed_subtitles", False),
            snip_start=options.get("snip_start"),
            snip_end=options.get("snip_end"),
            split_chapters=options.get("split_chapters", False),
        )

        self.queue_widget.add_task(task)

    def _on_playlist_download_selected(self, selected_entries: List[Dict[str, Any]]):
        options = self.options_panel.get_options_payload()
        self._download_entries(selected_entries, options)
        self.downloader_stack.setCurrentIndex(0)

    def _download_entries(self, entries: List[Dict[str, Any]], options: Dict[str, Any]):
        for entry in entries:
            task = DownloadTask(
                task_id=str(uuid.uuid4()),
                url=entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}",
                media_type=options["media_type"],
                format_choice=options["format_choice"],
                quality_choice=options["quality_choice"],
                save_path=options["save_path"],
                title=entry.get("title", "Video"),
                thumbnail_url=entry.get("thumbnail", ""),
                duration_formatted=entry.get("duration_formatted", ""),
                embed_thumbnail=options.get("embed_thumbnail", True),
                embed_metadata=options.get("embed_metadata", True),
                embed_subtitles=options.get("embed_subtitles", False),
            )
            self.queue_widget.add_task(task)

    def _on_task_finished(self, task: DownloadTask):
        self.history_widget.refresh()
