from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QRadioButton, QButtonGroup, QWidget
)
from PySide6.QtCore import Qt, Signal, QByteArray
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from typing import Dict, Any, Optional


class PreviewCard(QFrame):
    mode_changed = Signal(str)  # "video" or "playlist"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewCard")
        self.net_manager = QNetworkAccessManager(self)
        self.current_metadata: Optional[Dict[str, Any]] = None
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        # Thumbnail Label
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(180, 101)  # 16:9 ratio
        self.thumb_label.setStyleSheet("""
            QLabel {
                background-color: #0b0c10;
                border-radius: 8px;
                border: 1px solid #272a38;
            }
        """)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("No Thumbnail")
        layout.addWidget(self.thumb_label)

        # Info Layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        self.title_label = QLabel("Media Title")
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #ffffff;")

        # Badges row (Channel, Duration, Views)
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        self.uploader_label = QLabel("Channel")
        self.uploader_label.setObjectName("MutedLabel")
        self.uploader_label.setStyleSheet("font-weight: 600; color: #cbd5e1;")

        self.duration_badge = QLabel("00:00")
        self.duration_badge.setObjectName("Badge")

        self.views_badge = QLabel("0 views")
        self.views_badge.setObjectName("Badge")

        self.size_badge = QLabel("~0 MB")
        self.size_badge.setObjectName("Badge")
        self.size_badge.setStyleSheet("background-color: #1e293b; color: #38bdf8;")

        meta_row.addWidget(self.uploader_label)
        meta_row.addWidget(self.duration_badge)
        meta_row.addWidget(self.views_badge)
        meta_row.addWidget(self.size_badge)
        meta_row.addStretch()

        info_layout.addWidget(self.title_label)
        info_layout.addLayout(meta_row)

        # Mode Selection Row (for playlist links that also point to a video)
        self.mode_container = QWidget()
        mode_layout = QHBoxLayout(self.mode_container)
        mode_layout.setContentsMargins(0, 4, 0, 0)
        mode_layout.setSpacing(12)

        mode_desc = QLabel("Mode:")
        mode_desc.setObjectName("MutedLabel")
        
        self.btn_group = QButtonGroup(self)
        self.radio_single = QRadioButton("Single Video")
        self.radio_playlist = QRadioButton("Full Playlist")
        self.btn_group.addButton(self.radio_single)
        self.btn_group.addButton(self.radio_playlist)
        self.radio_single.setChecked(True)

        self.radio_single.toggled.connect(self._on_mode_toggled)

        mode_layout.addWidget(mode_desc)
        mode_layout.addWidget(self.radio_single)
        mode_layout.addWidget(self.radio_playlist)
        mode_layout.addStretch()

        info_layout.addWidget(self.mode_container)
        self.mode_container.setVisible(False)

        layout.addLayout(info_layout, 1)

    def set_metadata(self, data: Dict[str, Any]):
        self.current_metadata = data
        self.setVisible(True)

        is_playlist = data.get("type") == "playlist"
        title = data.get("title", "Untitled")
        uploader = data.get("uploader", "Unknown Channel")
        
        self.title_label.setText(title)
        self.uploader_label.setText(f"👤 {uploader}")

        if is_playlist:
            count = data.get("entries_count", 0)
            self.duration_badge.setText(f"📑 {count} videos")
            self.views_badge.setVisible(False)
            self.size_badge.setText(f"Playlist Preview")
            self.mode_container.setVisible(False)
        else:
            self.duration_badge.setText(f"⏱ {data.get('duration_formatted', '00:00')}")
            self.views_badge.setVisible(True)
            self.views_badge.setText(f"👁 {data.get('view_count_formatted', '')}")
            
            # Estimated size from best video quality
            best_size_str = "Auto size"
            if data.get("video_qualities"):
                best_size_str = data["video_qualities"][0].get("filesize_formatted", "Auto size")
            self.size_badge.setText(f"💾 {best_size_str}")

            # Check if this video is part of a playlist
            if "playlist_entries" in data or data.get("is_playlist_member"):
                self.mode_container.setVisible(True)
            else:
                self.mode_container.setVisible(False)

        # Load thumbnail
        thumb_url = data.get("thumbnail")
        if thumb_url:
            self._load_thumbnail(thumb_url)
        else:
            self.thumb_label.setText("No Thumbnail")

    def update_estimated_size(self, size_str: str):
        self.size_badge.setText(f"💾 {size_str}")

    def _load_thumbnail(self, url: str):
        self.thumb_label.setText("Loading...")
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
            else:
                self.thumb_label.setText("Thumb Error")
        else:
            self.thumb_label.setText("Thumb Error")
        reply.deleteLater()

    def _on_mode_toggled(self, checked: bool):
        mode = "video" if self.radio_single.isChecked() else "playlist"
        self.mode_changed.emit(mode)
