from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from typing import Dict, Any, Optional


class PreviewCard(QFrame):
    inspect_playlist_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PreviewCard")
        self.net_manager = QNetworkAccessManager(self)
        self.current_metadata: Optional[Dict[str, Any]] = None
        self.total_playlist_count = 0
        self.selected_playlist_count = 0
        self._setup_ui()
        self.setVisible(False)

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        # Thumbnail Label (16:9)
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(180, 101)
        self.thumb_label.setStyleSheet("""
            QLabel {
                background-color: #0b0c10;
                border-radius: 8px;
                border: 1px solid rgba(120, 130, 150, 0.25);
            }
        """)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setText("No Thumbnail")
        layout.addWidget(self.thumb_label)

        # Middle: Info Layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        self.title_label = QLabel("Media Title")
        self.title_label.setObjectName("PreviewTitle")
        self.title_label.setWordWrap(True)

        # Badges row (Channel, Duration, Views, Size)
        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)

        self.uploader_label = QLabel("Channel")
        self.uploader_label.setObjectName("PreviewUploader")

        self.duration_badge = QLabel("00:00")
        self.duration_badge.setObjectName("Badge")

        self.views_badge = QLabel("0 views")
        self.views_badge.setObjectName("Badge")

        self.size_badge = QLabel("~0 MB")
        self.size_badge.setObjectName("Badge")

        meta_row.addWidget(self.uploader_label)
        meta_row.addWidget(self.duration_badge)
        meta_row.addWidget(self.views_badge)
        meta_row.addWidget(self.size_badge)
        meta_row.addStretch()

        info_layout.addWidget(self.title_label)
        info_layout.addLayout(meta_row)
        info_layout.addStretch()

        layout.addLayout(info_layout, 1)

        # Right Side: Inspect Playlist Action Button (placed in the red box area)
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.btn_inspect = QPushButton("Inspect Playlist →")
        self.btn_inspect.setObjectName("SecondaryAccentButton")
        self.btn_inspect.setStyleSheet("""
            QPushButton {
                font-size: 13px;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 8px;
            }
        """)
        self.btn_inspect.clicked.connect(self.inspect_playlist_requested.emit)
        self.btn_inspect.setVisible(False)

        right_layout.addWidget(self.btn_inspect)
        layout.addWidget(self.right_container)

    def set_metadata(self, data: Dict[str, Any]):
        self.current_metadata = data
        self.setVisible(True)

        is_playlist = data.get("type") == "playlist"
        title = data.get("title", "Untitled")
        uploader = data.get("uploader", "Unknown Channel")
        
        self.title_label.setText(title)
        self.uploader_label.setText(f"👤 {uploader}")

        if is_playlist:
            self.total_playlist_count = data.get("entries_count", 0)
            self.selected_playlist_count = self.total_playlist_count
            self.duration_badge.setText(f"📑 {self.total_playlist_count} videos")
            self.views_badge.setVisible(False)
            self.size_badge.setText("Playlist")
            
            # Show the Inspect Playlist button
            self.btn_inspect.setText(f"Inspect Playlist ({self.total_playlist_count}) →")
            self.btn_inspect.setVisible(True)
        else:
            self.duration_badge.setText(f"⏱ {data.get('duration_formatted', '00:00')}")
            self.views_badge.setVisible(True)
            self.views_badge.setText(f"👁 {data.get('view_count_formatted', '')}")
            self.btn_inspect.setVisible(False)
            
            # Estimated size from best video quality
            best_size_str = "Auto size"
            if data.get("video_qualities"):
                best_size_str = data["video_qualities"][0].get("filesize_formatted", "Auto size")
            self.size_badge.setText(f"💾 {best_size_str}")

        # Load thumbnail
        thumb_url = data.get("thumbnail")
        if thumb_url:
            self._load_thumbnail(thumb_url)
        else:
            self.thumb_label.setText("No Thumbnail")

    def update_selection_count(self, selected_count: int, total_count: int):
        self.selected_playlist_count = selected_count
        self.total_playlist_count = total_count
        if selected_count == total_count:
            self.duration_badge.setText(f"📑 {total_count} videos")
            self.btn_inspect.setText(f"Inspect Playlist ({total_count}) →")
        else:
            self.duration_badge.setText(f"📑 {selected_count} of {total_count} selected")
            self.btn_inspect.setText(f"Selected: {selected_count}/{total_count} →")

    def update_estimated_size(self, size_str: str):
        if self.current_metadata and self.current_metadata.get("type") != "playlist":
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
                self.thumb_label.setText("No Preview")
        else:
            self.thumb_label.setText("No Preview")
        reply.deleteLater()
