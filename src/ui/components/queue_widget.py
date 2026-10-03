from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QRunnable, QThreadPool, QObject
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from ...core.downloader import DownloadTask, DownloadWorker
from ...core.history import HistoryManager
from ...core.config import AppConfig


class WorkerSignals(QObject):
    progress = Signal(dict)
    status_changed = Signal(str, str)  # task_id, status
    finished = Signal(str, bool)  # task_id, success


class TaskRunnable(QRunnable):
    def __init__(self, task: DownloadTask):
        super().__init__()
        self.task = task
        self.signals = WorkerSignals()
        self.worker = DownloadWorker(
            task=task,
            progress_callback=self._on_progress,
            status_callback=self._on_status
        )

    def _on_progress(self, data: dict):
        self.signals.progress.emit(data)

    def _on_status(self, task_id: str, status: str):
        self.signals.status_changed.emit(task_id, status)

    def run(self):
        success = self.worker.run()
        self.signals.finished.emit(self.task.task_id, success)


class QueueItemWidget(QFrame):
    cancel_requested = Signal(str)

    def __init__(self, task: DownloadTask, parent=None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("QueueItemCard")
        self.net_manager = QNetworkAccessManager(self)
        self._setup_ui()
        if self.task.thumbnail_url:
            self._load_thumbnail(self.task.thumbnail_url)

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(12)

        # 1. Left: Compact Thumbnail Preview (84x48)
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(84, 48)
        self.thumb_label.setStyleSheet("""
            QLabel {
                background-color: #0b0c10;
                border-radius: 6px;
                border: 1px solid rgba(120, 130, 150, 0.2);
            }
        """)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("🎬" if self.task.media_type == "video" else "🎵")
        main_layout.addWidget(self.thumb_label)

        # 2. Middle: Title, Progress Bar, Metrics
        middle_layout = QVBoxLayout()
        middle_layout.setSpacing(5)

        # Top line: Title + Chips
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.title_lbl = QLabel(self.task.title)
        self.title_lbl.setObjectName("QueueItemTitle")
        self.title_lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title_lbl.setWordWrap(False)

        fmt_text = f"{self.task.format_choice.upper()} {self.task.quality_choice}"
        self.fmt_badge = QLabel(fmt_text)
        self.fmt_badge.setObjectName("Badge")

        self.status_badge = QLabel("Queued")
        self.status_badge.setObjectName("Badge")

        top_row.addWidget(self.title_lbl, 1)
        top_row.addWidget(self.fmt_badge)
        top_row.addWidget(self.status_badge)
        middle_layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        middle_layout.addWidget(self.progress_bar)

        # Metrics row: Percent, Speed, ETA, Size
        self.metrics_row = QHBoxLayout()
        self.metrics_row.setSpacing(12)

        self.percent_lbl = QLabel("0%")
        self.percent_lbl.setStyleSheet("font-weight: 700; font-size: 11px;")

        self.speed_lbl = QLabel("⚡ -- MB/s")
        self.speed_lbl.setObjectName("MutedLabel")

        self.eta_lbl = QLabel("⏱ --:--")
        self.eta_lbl.setObjectName("MutedLabel")

        self.size_lbl = QLabel("💾 0 / 0 MB")
        self.size_lbl.setObjectName("MutedLabel")

        self.metrics_row.addWidget(self.percent_lbl)
        self.metrics_row.addWidget(self.speed_lbl)
        self.metrics_row.addWidget(self.eta_lbl)
        self.metrics_row.addWidget(self.size_lbl)
        self.metrics_row.addStretch()

        middle_layout.addLayout(self.metrics_row)
        main_layout.addLayout(middle_layout, 1)

        # 3. Right: Action Buttons
        self.action_layout = QVBoxLayout()
        self.action_layout.setSpacing(4)
        self.action_layout.setAlignment(Qt.AlignCenter)

        self.btn_open_file = QPushButton("▶ Open")
        self.btn_open_file.setObjectName("QueueActionBtn")
        self.btn_open_file.setVisible(False)
        self.btn_open_file.clicked.connect(self._on_open_file)

        self.btn_open_folder = QPushButton("📁 Folder")
        self.btn_open_folder.setObjectName("QueueActionBtn")
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.clicked.connect(self._on_open_folder)

        self.btn_cancel = QPushButton("✕ Cancel")
        self.btn_cancel.setObjectName("QueueActionBtn")
        self.btn_cancel.clicked.connect(self._on_cancel)

        self.action_layout.addWidget(self.btn_open_file)
        self.action_layout.addWidget(self.btn_open_folder)
        self.action_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(self.action_layout)

    def _load_thumbnail(self, url: str):
        req = QNetworkRequest(url)
        reply = self.net_manager.get(req)
        reply.finished.connect(lambda: self._on_thumb_reply(reply))

    def _on_thumb_reply(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            img_data = reply.readAll()
            image = QImage()
            if image.loadFromData(img_data):
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(
                    self.thumb_label.size(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                self.thumb_label.setPixmap(scaled)
        reply.deleteLater()

    def update_progress(self, data: dict):
        prog = int(data.get("progress", 0))
        self.progress_bar.setValue(prog)
        self.percent_lbl.setText(f"{prog}%")

        speed = data.get("speed", "-- MB/s")
        eta = data.get("eta", "--:--")
        size = data.get("size", "")

        self.speed_lbl.setText(f"⚡ {speed}")
        self.eta_lbl.setText(f"⏱ {eta}")
        if size:
            self.size_lbl.setText(f"💾 {size}")

    def update_status(self, status: str):
        if status == "downloading":
            self.status_badge.setText("Downloading")
            self.status_badge.setStyleSheet("background-color: rgba(56, 189, 248, 0.15); color: #38bdf8;")
        elif status == "converting":
            self.status_badge.setText("Converting...")
            self.status_badge.setStyleSheet("background-color: rgba(234, 179, 8, 0.15); color: #facc15;")
            self.speed_lbl.setText("Applying tags & muxing...")
        elif status == "finished":
            self.status_badge.setText("Completed")
            self.status_badge.setStyleSheet("background-color: rgba(16, 185, 129, 0.15); color: #34d399;")
            self.progress_bar.setValue(100)
            self.percent_lbl.setText("100%")
            self.speed_lbl.setText("Download complete")
            self.btn_cancel.setVisible(False)
            self.btn_open_file.setVisible(True)
            self.btn_open_folder.setVisible(True)
        elif status == "cancelled":
            self.status_badge.setText("Cancelled")
            self.status_badge.setStyleSheet("background-color: rgba(148, 163, 184, 0.15); color: #94a3b8;")
            self.btn_cancel.setEnabled(False)
            self.speed_lbl.setText("Cancelled by user")
        elif status == "error":
            self.status_badge.setText("Failed")
            self.status_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #f87171;")
            self.btn_cancel.setEnabled(False)
            err = self.task.error_message or "Download error"
            self.speed_lbl.setText(err[:50] + "..." if len(err) > 50 else err)

    def _on_cancel(self):
        self.task.cancel()
        self.update_status("cancelled")
        self.cancel_requested.emit(self.task.task_id)

    def _on_open_file(self):
        if self.task.output_file:
            HistoryManager.open_file(self.task.output_file)

    def _on_open_folder(self):
        if self.task.output_file:
            HistoryManager.open_folder(self.task.output_file)
        elif self.task.save_path:
            HistoryManager.open_folder(self.task.save_path)


class QueueWidget(QWidget):
    task_finished_signal = Signal(object)  # DownloadTask

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks: Dict[str, DownloadTask] = {}
        self.item_widgets: Dict[str, QueueItemWidget] = {}
        self.runnables: Dict[str, TaskRunnable] = {}

        self.thread_pool = QThreadPool.globalInstance()
        cfg = AppConfig.get_instance()
        max_concurrent = cfg.get("max_concurrent_downloads", 3)
        self.thread_pool.setMaxThreadCount(max_concurrent)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Header with Clear Completed button
        header = QHBoxLayout()
        self.queue_title = QLabel("Download Queue (0 active)")
        self.queue_title.setObjectName("SectionTitle")

        self.btn_clear_completed = QPushButton("Clear Completed")
        self.btn_clear_completed.clicked.connect(self.clear_completed)

        header.addWidget(self.queue_title)
        header.addStretch()
        header.addWidget(self.btn_clear_completed)

        layout.addLayout(header)

        # Scroll Area for active tasks
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(8)

        # Sleek Empty State placeholder
        self.empty_placeholder = QFrame()
        self.empty_placeholder.setObjectName("Card")
        self.empty_placeholder.setStyleSheet("""
            QFrame {
                border: 1.5px dashed rgba(120, 130, 160, 0.25);
                border-radius: 10px;
                padding: 24px;
            }
        """)
        empty_layout = QVBoxLayout(self.empty_placeholder)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(6)

        empty_icon = QLabel("📥")
        empty_icon.setStyleSheet("font-size: 26px;")
        empty_icon.setAlignment(Qt.AlignCenter)

        empty_title = QLabel("No Active Downloads")
        empty_title.setObjectName("SectionTitle")
        empty_title.setAlignment(Qt.AlignCenter)

        empty_sub = QLabel("Paste a YouTube link above and click Download Now or Add to Queue.")
        empty_sub.setObjectName("MutedLabel")
        empty_sub.setAlignment(Qt.AlignCenter)

        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(empty_title)
        empty_layout.addWidget(empty_sub)

        self.scroll_layout.addWidget(self.empty_placeholder)
        self.scroll_layout.addStretch()

        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll, 1)

    def add_task(self, task: DownloadTask):
        self.empty_placeholder.setVisible(False)
        self.tasks[task.task_id] = task

        item_widget = QueueItemWidget(task)
        item_widget.cancel_requested.connect(self._on_task_cancelled)
        self.item_widgets[task.task_id] = item_widget

        # Insert right above stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, item_widget)
        self._update_title()

        # Create and start Runnable
        runnable = TaskRunnable(task)
        runnable.signals.progress.connect(self._on_task_progress)
        runnable.signals.status_changed.connect(self._on_task_status_changed)
        runnable.signals.finished.connect(self._on_task_finished)
        self.runnables[task.task_id] = runnable

        self.thread_pool.start(runnable)

    def _on_task_progress(self, data: dict):
        task_id = data.get("task_id")
        if task_id in self.item_widgets:
            self.item_widgets[task_id].update_progress(data)

    def _on_task_status_changed(self, task_id: str, status: str):
        if task_id in self.item_widgets:
            self.item_widgets[task_id].update_status(status)

    def _on_task_finished(self, task_id: str, success: bool):
        task = self.tasks.get(task_id)
        if not task:
            return

        if success and task.status != "cancelled":
            if task_id in self.item_widgets:
                self.item_widgets[task_id].update_status("finished")
            
            # Save to history
            HistoryManager.get_instance().add_entry(
                title=task.title,
                url=task.url,
                media_type=task.media_type,
                format_choice=task.format_choice,
                file_path=task.output_file,
                thumbnail_url=task.thumbnail_url,
                duration=task.duration_formatted,
            )
            self.task_finished_signal.emit(task)

        self._update_title()

    def _on_task_cancelled(self, task_id: str):
        self._update_title()

    def clear_completed(self):
        to_remove = []
        for tid, task in self.tasks.items():
            if task.status in ["finished", "cancelled", "error"]:
                to_remove.append(tid)

        for tid in to_remove:
            if tid in self.item_widgets:
                widget = self.item_widgets.pop(tid)
                self.scroll_layout.removeWidget(widget)
                widget.deleteLater()
            self.tasks.pop(tid, None)
            self.runnables.pop(tid, None)

        if not self.tasks:
            self.empty_placeholder.setVisible(True)

        self._update_title()

    def _update_title(self):
        active_count = sum(1 for t in self.tasks.values() if t.status in ["queued", "downloading", "converting"])
        self.queue_title.setText(f"Download Queue ({active_count} active)")
        if not self.tasks:
            self.empty_placeholder.setVisible(True)
