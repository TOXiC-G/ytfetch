from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QAbstractItemView
)
from PySide6.QtCore import Signal, Qt
from typing import List, Dict, Any, Optional


class PlaylistView(QWidget):
    download_selected_requested = Signal(list)  # list of selected entry dicts

    def __init__(self, parent=None):
        super().__init__(parent)
        self.entries: List[Dict[str, Any]] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Top Control Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.info_label = QLabel("Playlist Items (0)")
        self.info_label.setObjectName("SectionTitle")

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter videos by keyword...")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self._filter_table)
        self.search_edit.setMaximumWidth(250)

        self.btn_select_all = QPushButton("Select All")
        self.btn_select_all.clicked.connect(self._select_all)

        self.btn_deselect_all = QPushButton("Deselect All")
        self.btn_deselect_all.clicked.connect(self._deselect_all)

        self.btn_invert = QPushButton("Invert")
        self.btn_invert.clicked.connect(self._invert_selection)

        top_bar.addWidget(self.info_label)
        top_bar.addStretch()
        top_bar.addWidget(self.search_edit)
        top_bar.addWidget(self.btn_select_all)
        top_bar.addWidget(self.btn_deselect_all)
        top_bar.addWidget(self.btn_invert)

        layout.addLayout(top_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["", "#", "Title", "Duration"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        layout.addWidget(self.table, 1)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()
        self.selection_summary = QLabel("Selected: 0 / 0")
        self.selection_summary.setObjectName("MutedLabel")

        self.btn_download_selected = QPushButton("⬇ Download Selected")
        self.btn_download_selected.setObjectName("PrimaryButton")
        self.btn_download_selected.clicked.connect(self._on_download_selected)

        bottom_bar.addWidget(self.selection_summary)
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.btn_download_selected)

        layout.addLayout(bottom_bar)

    def load_playlist(self, playlist_data: Dict[str, Any]):
        self.entries = playlist_data.get("entries", [])
        self.info_label.setText(f"📑 {playlist_data.get('title', 'Playlist')} ({len(self.entries)} videos)")
        self._populate_table()

    def _populate_table(self):
        self.table.setRowCount(len(self.entries))
        for row, entry in enumerate(self.entries):
            # Checkbox item
            chk = QCheckBox()
            chk.setChecked(entry.get("selected", True))
            chk.stateChanged.connect(lambda state, r=row: self._on_checkbox_changed(r, state))
            
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.setContentsMargins(8, 0, 8, 0)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.addWidget(chk)
            self.table.setCellWidget(row, 0, chk_widget)

            # Index
            idx_item = QTableWidgetItem(str(entry.get("index", row + 1)))
            idx_item.setTextAlignment(Qt.AlignCenter)
            idx_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 1, idx_item)

            # Title
            title_item = QTableWidgetItem(entry.get("title", "Untitled"))
            title_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 2, title_item)

            # Duration
            dur_item = QTableWidgetItem(entry.get("duration_formatted", "00:00"))
            dur_item.setTextAlignment(Qt.AlignCenter)
            dur_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(row, 3, dur_item)

        self._update_summary()

    def _on_checkbox_changed(self, row: int, state: int):
        if row < len(self.entries):
            self.entries[row]["selected"] = (state == Qt.Checked)
        self._update_summary()

    def _select_all(self):
        for row in range(self.table.rowCount()):
            chk_widget = self.table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(True)
        for e in self.entries:
            e["selected"] = True
        self._update_summary()

    def _deselect_all(self):
        for row in range(self.table.rowCount()):
            chk_widget = self.table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(False)
        for e in self.entries:
            e["selected"] = False
        self._update_summary()

    def _invert_selection(self):
        for row in range(self.table.rowCount()):
            chk_widget = self.table.cellWidget(row, 0)
            if chk_widget:
                chk = chk_widget.findChild(QCheckBox)
                if chk:
                    chk.setChecked(not chk.isChecked())
                    if row < len(self.entries):
                        self.entries[row]["selected"] = chk.isChecked()
        self._update_summary()

    def _filter_table(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 2)
            if item:
                matched = (query in item.text().lower()) if query else True
                self.table.setRowHidden(row, not matched)

    def _update_summary(self):
        selected_count = sum(1 for e in self.entries if e.get("selected", True))
        self.selection_summary.setText(f"Selected: {selected_count} / {len(self.entries)} videos")

    def _on_download_selected(self):
        selected = [e for e in self.entries if e.get("selected", True)]
        if selected:
            self.download_selected_requested.emit(selected)
