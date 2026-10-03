import os
import re
from pathlib import Path
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QComboBox,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QWidget
)
from PySide6.QtCore import Signal, Qt
from typing import Dict, Any, Optional

from ...core.config import AppConfig


class OptionsPanel(QFrame):
    download_now_requested = Signal(dict)
    add_queue_requested = Signal(dict)
    options_changed = Signal(str)  # emits estimated size string

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OptionsCard")
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.is_playlist = False
        self.selected_item_count = 1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # 1. Format & Quality Grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(10)

        # Media Type
        lbl_type = QLabel("Media Type:")
        lbl_type.setObjectName("SectionTitle")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Video (MP4/MKV/WebM)", "Audio (MP3/FLAC/M4A)"])
        self.combo_type.currentIndexChanged.connect(self._on_type_changed)

        # Format
        lbl_format = QLabel("Container / Codec:")
        lbl_format.setObjectName("SectionTitle")
        self.combo_format = QComboBox()
        self.combo_format.currentIndexChanged.connect(self._on_format_changed)

        # Quality / Bitrate
        self.lbl_quality = QLabel("Quality / Resolution:")
        self.lbl_quality.setObjectName("SectionTitle")
        self.combo_quality = QComboBox()
        self.combo_quality.currentIndexChanged.connect(self._on_quality_changed)

        grid.addWidget(lbl_type, 0, 0)
        grid.addWidget(self.combo_type, 0, 1)
        grid.addWidget(lbl_format, 0, 2)
        grid.addWidget(self.combo_format, 0, 3)
        grid.addWidget(self.lbl_quality, 0, 4)
        grid.addWidget(self.combo_quality, 0, 5)

        layout.addLayout(grid)

        # 2. Checkboxes Row
        checks_layout = QHBoxLayout()
        checks_layout.setSpacing(16)

        self.chk_thumb = QCheckBox("Embed Artwork")
        self.chk_thumb.setChecked(True)

        self.chk_meta = QCheckBox("Embed Metadata Tags")
        self.chk_meta.setChecked(True)

        self.chk_subs = QCheckBox("Embed Subtitles")
        self.chk_subs.setChecked(False)

        self.chk_chapters = QCheckBox("Split Chapters")
        self.chk_chapters.setChecked(False)
        self.chk_chapters.setEnabled(False)

        self.chk_snip = QCheckBox("Snip Range")
        self.chk_snip.setChecked(False)
        self.chk_snip.toggled.connect(self._on_snip_toggled)

        checks_layout.addWidget(self.chk_thumb)
        checks_layout.addWidget(self.chk_meta)
        checks_layout.addWidget(self.chk_subs)
        checks_layout.addWidget(self.chk_chapters)
        checks_layout.addWidget(self.chk_snip)
        checks_layout.addStretch()

        layout.addLayout(checks_layout)

        # 3. Snipping Time Range Row (hidden by default)
        self.snip_container = QWidget()
        snip_layout = QHBoxLayout(self.snip_container)
        snip_layout.setContentsMargins(0, 0, 0, 0)
        snip_layout.setSpacing(10)

        snip_lbl = QLabel("Snip Range:")
        snip_lbl.setObjectName("MutedLabel")
        self.snip_start_edit = QLineEdit("00:00:00")
        self.snip_start_edit.setPlaceholderText("Start (HH:MM:SS)")
        self.snip_start_edit.setMaximumWidth(120)

        to_lbl = QLabel("to")
        to_lbl.setObjectName("MutedLabel")

        self.snip_end_edit = QLineEdit("00:00:00")
        self.snip_end_edit.setPlaceholderText("End (HH:MM:SS)")
        self.snip_end_edit.setMaximumWidth(120)

        snip_layout.addWidget(snip_lbl)
        snip_layout.addWidget(self.snip_start_edit)
        snip_layout.addWidget(to_lbl)
        snip_layout.addWidget(self.snip_end_edit)
        snip_layout.addStretch()

        self.snip_container.setVisible(False)
        layout.addWidget(self.snip_container)

        # 4. Playlist Subfolder Selection Row (Clean & defaulted to True when playlist)
        self.playlist_folder_container = QWidget()
        pl_folder_layout = QHBoxLayout(self.playlist_folder_container)
        pl_folder_layout.setContentsMargins(0, 0, 0, 0)
        pl_folder_layout.setSpacing(10)

        self.chk_playlist_folder = QCheckBox("Save into playlist folder:")
        self.chk_playlist_folder.setChecked(True)
        self.chk_playlist_folder.toggled.connect(self._on_playlist_folder_toggled)

        self.folder_name_edit = QLineEdit("Playlist")
        self.folder_name_edit.setPlaceholderText("Folder name")

        pl_folder_layout.addWidget(self.chk_playlist_folder)
        pl_folder_layout.addWidget(self.folder_name_edit, 1)

        self.playlist_folder_container.setVisible(False)
        layout.addWidget(self.playlist_folder_container)

        # 5. Save Location & Actions Row
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        loc_lbl = QLabel("Save To:")
        loc_lbl.setObjectName("MutedLabel")

        cfg = AppConfig.get_instance()
        default_dir = cfg.get("download_path", str(Path.home() / "Downloads" / "ytfetch"))

        self.path_edit = QLineEdit(default_dir)
        self.path_edit.setReadOnly(True)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse_clicked)

        self.btn_queue = QPushButton("+ Add to Queue")
        self.btn_queue.setObjectName("SecondaryAccentButton")
        self.btn_queue.clicked.connect(self._on_queue_clicked)

        # Clean, modern download button without cheap emoji
        self.btn_download = QPushButton("Download Now")
        self.btn_download.setObjectName("PrimaryButton")
        self.btn_download.clicked.connect(self._on_download_clicked)

        bottom_row.addWidget(loc_lbl)
        bottom_row.addWidget(self.path_edit, 1)
        bottom_row.addWidget(self.browse_btn)
        bottom_row.addWidget(self.btn_queue)
        bottom_row.addWidget(self.btn_download)

        layout.addLayout(bottom_row)

        self._populate_video_options()

    def set_metadata(self, data: Dict[str, Any]):
        self.current_metadata = data
        self.is_playlist = (data.get("type") == "playlist")

        if self.is_playlist:
            count = data.get("entries_count", 0)
            self.selected_item_count = count
            self.playlist_folder_container.setVisible(True)
            self.chk_playlist_folder.setChecked(True)

            # Default folder name to playlist title or first video title
            folder_title = data.get("title", "")
            if not folder_title or folder_title == "YouTube Playlist":
                entries = data.get("entries", [])
                if entries:
                    folder_title = entries[0].get("title", "Playlist")
            
            clean_name = self._sanitize_folder_name(folder_title)
            self.folder_name_edit.setText(clean_name or "Playlist")
            self._update_button_labels()
        else:
            self.playlist_folder_container.setVisible(False)
            self.selected_item_count = 1
            self._update_button_labels()

        chapters = data.get("chapters", [])
        if chapters:
            self.chk_chapters.setEnabled(True)
            self.chk_chapters.setText(f"Split Chapters ({len(chapters)})")
        else:
            self.chk_chapters.setEnabled(False)
            self.chk_chapters.setText("Split Chapters")
            self.chk_chapters.setChecked(False)

        self._on_type_changed(self.combo_type.currentIndex())

    def update_selected_count(self, count: int):
        self.selected_item_count = count
        self._update_button_labels()

    def _update_button_labels(self):
        if self.is_playlist:
            self.btn_download.setText(f"Download Now ({self.selected_item_count})")
            self.btn_queue.setText(f"+ Add to Queue ({self.selected_item_count})")
        else:
            self.btn_download.setText("Download Now")
            self.btn_queue.setText("+ Add to Queue")

    def _sanitize_folder_name(self, name: str) -> str:
        # Strip invalid Windows filename characters: \ / : * ? " < > |
        cleaned = re.sub(r'[\\/*?:"<>|]', '', name).strip()
        return cleaned[:80] if len(cleaned) > 80 else cleaned

    def _on_playlist_folder_toggled(self, checked: bool):
        self.folder_name_edit.setEnabled(checked)

    def _on_type_changed(self, index: int):
        is_video = (index == 0)
        self.chk_subs.setEnabled(is_video)

        self.combo_format.blockSignals(True)
        self.combo_format.clear()
        if is_video:
            self.lbl_quality.setText("Quality / Resolution:")
            self.combo_format.addItems(["MP4", "MKV", "WebM"])
            self._populate_video_options()
        else:
            self.lbl_quality.setText("Audio Bitrate:")
            self.combo_format.addItems(["MP3", "M4A", "FLAC", "WAV", "OGG"])
            self._populate_audio_options()
        self.combo_format.blockSignals(False)
        self._emit_size_update()

    def _populate_video_options(self):
        self.combo_quality.blockSignals(True)
        self.combo_quality.clear()
        if self.current_metadata and self.current_metadata.get("video_qualities"):
            for q in self.current_metadata["video_qualities"]:
                size_str = q.get("filesize_formatted", "")
                text = f"{q['label']} ({size_str})" if size_str else q["label"]
                self.combo_quality.addItem(text, userData=q)
        else:
            self.combo_quality.addItem("Best Available (~Auto)", userData={"height": 9999, "format_id": "best", "filesize_formatted": "Auto"})
            self.combo_quality.addItem("1080p (FHD)", userData={"height": 1080, "format_id": "1080", "filesize_formatted": "1080p"})
            self.combo_quality.addItem("720p (HD)", userData={"height": 720, "format_id": "720", "filesize_formatted": "720p"})
            self.combo_quality.addItem("480p (SD)", userData={"height": 480, "format_id": "480", "filesize_formatted": "480p"})
        self.combo_quality.blockSignals(False)

    def _populate_audio_options(self):
        self.combo_quality.blockSignals(True)
        self.combo_quality.clear()
        if self.current_metadata and self.current_metadata.get("audio_qualities"):
            for a in self.current_metadata["audio_qualities"]:
                size_str = a.get("filesize_formatted", "")
                text = f"{a['label']} ({size_str})" if size_str else a["label"]
                self.combo_quality.addItem(text, userData=a)
        else:
            self.combo_quality.addItem("320 kbps (High Quality)", userData={"bitrate": "320k", "filesize_formatted": "~320k"})
            self.combo_quality.addItem("256 kbps (Medium)", userData={"bitrate": "256k", "filesize_formatted": "~256k"})
            self.combo_quality.addItem("192 kbps (Standard)", userData={"bitrate": "192k", "filesize_formatted": "~192k"})
            self.combo_quality.addItem("128 kbps (Compact)", userData={"bitrate": "128k", "filesize_formatted": "~128k"})
        self.combo_quality.blockSignals(False)

    def _on_format_changed(self):
        self._emit_size_update()

    def _on_quality_changed(self):
        self._emit_size_update()

    def _emit_size_update(self):
        data = self.combo_quality.currentData()
        if data and isinstance(data, dict):
            size_str = data.get("filesize_formatted", "Auto")
            self.options_changed.emit(size_str)

    def _on_snip_toggled(self, checked: bool):
        self.snip_container.setVisible(checked)
        if checked and self.current_metadata:
            duration_str = self.current_metadata.get("duration_formatted", "00:00:00")
            if duration_str.count(":") == 1:
                duration_str = "00:" + duration_str
            self.snip_end_edit.setText(duration_str)

    def _on_browse_clicked(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.path_edit.text())
        if dir_path:
            self.path_edit.setText(dir_path)
            AppConfig.get_instance().set("download_path", dir_path)

    def get_options_payload(self) -> Dict[str, Any]:
        is_video = (self.combo_type.currentIndex() == 0)
        qdata = self.combo_quality.currentData() or {}

        quality_choice = "best"
        format_id = None
        if is_video:
            tier = qdata.get("tier")
            h = qdata.get("height")
            format_id = qdata.get("format_id")
            val = tier or h
            quality_choice = "best" if (not val or val == 9999) else str(val)
        else:
            quality_choice = qdata.get("bitrate", "320k")

        base_save_path = self.path_edit.text().strip()
        # If playlist and subfolder is checked, nest path into folder
        if self.is_playlist and self.chk_playlist_folder.isChecked():
            subfolder = self._sanitize_folder_name(self.folder_name_edit.text().strip()) or "Playlist"
            final_save_path = os.path.join(base_save_path, subfolder)
        else:
            final_save_path = base_save_path

        return {
            "media_type": "video" if is_video else "audio",
            "format_choice": self.combo_format.currentText().lower(),
            "quality_choice": quality_choice,
            "format_id": format_id,
            "save_path": final_save_path,
            "embed_thumbnail": self.chk_thumb.isChecked(),
            "embed_metadata": self.chk_meta.isChecked(),
            "embed_subtitles": self.chk_subs.isChecked() if is_video else False,
            "split_chapters": self.chk_chapters.isChecked(),
            "snip_start": self.snip_start_edit.text().strip() if self.chk_snip.isChecked() else None,
            "snip_end": self.snip_end_edit.text().strip() if self.chk_snip.isChecked() else None,
        }

    def _on_download_clicked(self):
        payload = self.get_options_payload()
        self.download_now_requested.emit(payload)

    def _on_queue_clicked(self):
        payload = self.get_options_payload()
        self.add_queue_requested.emit(payload)
