import uuid
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar,
    QScrollArea, QFrame
)
from PySide6.QtCore import Signal, Qt, QRunnable, QThreadPool, QObject

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
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header Row: Title + Format Badge + Status Badge
        header = QHBoxLayout()
        header.setSpacing(8)

        self.title_lbl = QLabel(self.task.title)
        self.title_lbl.setStyleSheet("font-weight: 600; font-size: 13px; color: #ffffff;")
        self.title_lbl.setWordWrap(False)

        fmt_text = f"{self.task.format_choice.upper()} {self.task.quality_choice}"
        self.fmt_badge = QLabel(fmt_text)
        self.fmt_badge.setObjectName("Badge")

        self.status_badge = QLabel("Queued")
        self.status_badge.setObjectName("Badge")

        header.addWidget(self.title_lbl, 1)
        header.addWidget(self.fmt_badge)
        header.addWidget(self.status_badge)

        layout.addLayout(header)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Bottom info row: Speed, ETA, Size + Cancel/Open Buttons
        bottom = QHBoxLayout()
        bottom.setSpacing(10)

        self.info_lbl = QLabel("Waiting in queue...")
        self.info_lbl.setObjectName("MutedLabel")

        self.btn_open_file = QPushButton("▶ Open")
        self.btn_open_file.setVisible(False)
        self.btn_open_file.clicked.connect(self._on_open_file)

        self.btn_open_folder = QPushButton("📁 Folder")
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.clicked.connect(self._on_open_folder)

        self.btn_cancel = QPushButton("✕ Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel)

        bottom.addWidget(self.info_lbl, 1)
        bottom.addWidget(self.btn_open_file)
        bottom.addWidget(self.btn_open_folder)
        bottom.addWidget(self.btn_cancel)

        layout.addLayout(bottom)

    def update_progress(self, data: dict):
        prog = int(data.get("progress", 0))
        self.progress_bar.setValue(prog)
        speed = data.get("speed", "-- MB/s")
        eta = data.get("eta", "--:--")
        size = data.get("size", "")
        self.info_lbl.setText(f"{prog}% | {speed} | ETA: {eta} | {size}")

    def update_status(self, status: str):
        if status == "downloading":
            self.status_badge.setText("Downloading")
            self.status_badge.setStyleSheet("background-color: rgba(56, 189, 248, 0.15); color: #38bdf8;")
        elif status == "converting":
            self.status_badge.setText("Converting...")
            self.status_badge.setStyleSheet("background-color: rgba(234, 179, 8, 0.15); color: #facc15;")
            self.info_lbl.setText("Muxing and applying tags/artwork...")
        elif status == "finished":
            self.status_badge.setText("Completed")
            self.status_badge.setStyleSheet("background-color: rgba(16, 185, 129, 0.15); color: #34d399;")
            self.progress_bar.setValue(100)
            self.info_lbl.setText("Finished")
            self.btn_cancel.setVisible(False)
            self.btn_open_file.setVisible(True)
            self.btn_open_folder.setVisible(True)
        elif status == "cancelled":
            self.status_badge.setText("Cancelled")
            self.status_badge.setStyleSheet("background-color: rgba(148, 163, 184, 0.15); color: #94a3b8;")
            self.btn_cancel.setEnabled(False)
            self.info_lbl.setText("Cancelled by user")
        elif status == "error":
            self.status_badge.setText("Error")
            self.status_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #f87171;")
            self.btn_cancel.setEnabled(False)
            err = self.task.error_message or "Download error occurred"
            self.info_lbl.setText(err[:60] + "..." if len(err) > 60 else err)

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
        self.queue_title = QLabel("Download Queue (0)")
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

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.addStretch()

        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll, 1)

    def add_task(self, task: DownloadTask):
        self.tasks[task.task_id] = task

        item_widget = QueueItemWidget(task)
        item_widget.cancel_requested.connect(self._on_task_cancelled)
        self.item_widgets[task.task_id] = item_widget

        # Insert before stretch
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

        self._update_title()

    def _update_title(self):
        active_count = sum(1 for t in self.tasks.values() if t.status in ["queued", "downloading", "converting"])
        self.queue_title.setText(f"Download Queue ({active_count} active)")
