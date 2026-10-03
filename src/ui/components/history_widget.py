import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt
from typing import List, Dict, Any

from ...core.history import HistoryManager
from ...core.extractor import MediaMetadataExtractor


class HistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_mgr = HistoryManager.get_instance()
        self.entries: List[Dict[str, Any]] = []
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header bar
        header = QHBoxLayout()
        self.title_lbl = QLabel("Download History")
        self.title_lbl.setObjectName("SectionTitle")

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search history...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._filter_table)
        self.search_edit.setMaximumWidth(220)

        self.btn_refresh = QPushButton("⟳ Refresh")
        self.btn_refresh.clicked.connect(self.refresh)

        self.btn_clear = QPushButton("Clear History")
        self.btn_clear.clicked.connect(self._on_clear_clicked)

        header.addWidget(self.title_lbl)
        header.addStretch()
        header.addWidget(self.search_edit)
        header.addWidget(self.btn_refresh)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # History Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Format", "Size", "Date", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        layout.addWidget(self.table, 1)

    def refresh(self):
        self.entries = self.history_mgr.get_all()
        self.table.setRowCount(len(self.entries))

        for row, entry in enumerate(self.entries):
            # Title
            title_text = entry.get("title", "Untitled")
            title_item = QTableWidgetItem(title_text)
            title_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 0, title_item)

            # Format
            fmt_text = f"{entry.get('media_type', '').upper()} ({entry.get('format', '').upper()})"
            fmt_item = QTableWidgetItem(fmt_text)
            fmt_item.setTextAlignment(Qt.AlignCenter)
            fmt_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 1, fmt_item)

            # Size
            size_bytes = entry.get("file_size", 0)
            size_str = MediaMetadataExtractor.format_size(size_bytes)
            size_item = QTableWidgetItem(size_str)
            size_item.setTextAlignment(Qt.AlignCenter)
            size_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 2, size_item)

            # Date
            created_at = entry.get("created_at", time.time())
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(created_at))
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            date_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 3, date_item)

            # Action Buttons Widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(6)

            file_path = entry.get("file_path", "")
            exists = entry.get("exists", False)

            btn_open = QPushButton("▶ Open")
            btn_open.setEnabled(exists)
            btn_open.clicked.connect(lambda _, fp=file_path: HistoryManager.open_file(fp))

            btn_folder = QPushButton("📁 Folder")
            btn_folder.setEnabled(exists)
            btn_folder.clicked.connect(lambda _, fp=file_path: HistoryManager.open_folder(fp))

            btn_del = QPushButton("✕")
            btn_del.setToolTip("Delete from history")
            entry_id = entry.get("id")
            btn_del.clicked.connect(lambda _, eid=entry_id: self._on_delete_entry(eid))

            actions_layout.addWidget(btn_open)
            actions_layout.addWidget(btn_folder)
            actions_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 4, actions_widget)

    def _filter_table(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                matched = (query in item.text().lower()) if query else True
                self.table.setRowHidden(row, not matched)

    def _on_delete_entry(self, entry_id: int):
        self.history_mgr.delete_entry(entry_id)
        self.refresh()

    def _on_clear_clicked(self):
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all download history records? (Files on disk will not be deleted)",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_mgr.clear_all()
            self.refresh()
