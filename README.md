# ⚡ ApexLoad

> **Modern, High-Performance YouTube Downloader & Media Converter for Windows**

ApexLoad is a sleek, hardware-accelerated desktop application built with **PySide6 (Qt 6)**, **yt-dlp**, and **FFmpeg**. It combines raw command-line speed and precision with a rich, responsive interface designed for 60 FPS performance on Windows 10 and 11.

---

## ✨ Features

- 🎯 **Clean & Canonical Links**: Automatically strips tracking & telemetry query params (`?si=`, `&feature=`, etc.).
- 📋 **Live Clipboard Auto-Detection**: Detects copied YouTube links and prompts to fetch with a single click.
- 🎬 **Multi-Format Video Downloads**: MP4, MKV, WebM in up to 4K (2160p), 1440p, 1080p 60fps, 720p, with dynamic size estimation.
- 🎵 **Studio-Grade Audio Extraction**: Convert videos into high-bitrate MP3 (320 kbps), Lossless FLAC, M4A, WAV, or OGG.
- 🎨 **Automatic Artwork & Metadata Tagging**: Embeds high-resolution thumbnail as album artwork, populates Title, Artist/Channel, and Year into ID3/MP4 tags.
- 📑 **Playlist Inspector**: Browse full playlists with thumbnail previews, durations, search filtering, and selective batch downloading.
- ✂️ **Time Snipping & Chapters**: Download specific time ranges or split audio/video into separate tagged chapter tracks.
- 🚀 **Lag-Free Threaded Queue**: Background worker pool (`QThreadPool`) with live progress, transfer speed (MB/s), ETA timer, pause/resume, and cancellation.
- 🕒 **Download History**: Local SQLite history tracking with one-click "Open File" and "Open in Explorer" actions.
- 🌙 **Dark & Light Mode**: Tailored dark slate aesthetic with radiant accents and full light mode toggle.
- ⚙️ **Self-Managing Dependencies**: Auto-detects system and WinGet FFmpeg; one-click updater for the `yt-dlp` extraction engine.

---

## 🛠️ Project Structure

```
yt-download/
├── .venv/                      # Python 3.11 virtual environment
├── .github/
│   └── workflows/
│       └── release.yml         # GitHub Actions automated release pipeline
├── installer/
│   ├── installer.iss           # Inno Setup Windows installer script
│   └── apexload.ico            # Multi-resolution application icon
├── src/
│   ├── main.py                 # Application entry point & Qt loop
│   ├── core/
│   │   ├── config.py           # Configuration manager
│   │   ├── sanitizer.py        # URL cleaner & smart detector
│   │   ├── ffmpeg_mgr.py       # FFmpeg/FFprobe locator & fallback
│   │   ├── extractor.py        # yt-dlp metadata extraction & size calculator
│   │   ├── downloader.py       # Threaded download worker & progress hooks
│   │   ├── history.py          # SQLite history storage & shell launcher
│   │   └── updater.py          # yt-dlp engine self-updater
│   ├── ui/
│   │   ├── theme.py            # Dark & Light QSS stylesheets
│   │   ├── main_window.py      # Main window & layout coordination
│   │   └── components/
│   │       ├── url_input_bar.py    # URL bar with clipboard toast
│   │       ├── preview_card.py     # Video thumbnail, duration, badges
│   │       ├── options_panel.py    # Format, bitrate, resolution, snipping
│   │       ├── playlist_view.py    # Playlist table & bulk selection
│   │       ├── queue_widget.py     # Concurrent download queue
│   │       ├── history_widget.py   # Download history table
│   │       └── settings_dialog.py  # App settings & engine status
│   └── assets/
│       └── apexload.ico        # App icon
├── tests/
│   ├── test_sanitizer.py       # URL cleaner tests
│   └── test_history.py         # History & FFmpeg tests
├── requirements.txt            # Python dependencies
├── ApexLoad.spec               # PyInstaller build specification
└── README.md
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+** installed on Windows.
- **FFmpeg** (Recommended: installed via `winget install Gyan.FFmpeg`, or managed via local portable download in settings).

### 2. Virtual Environment Setup
```powershell
# Clone or navigate to the repository
cd h:\Dev\yt-download

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt
```

### 3. Launching the App
```powershell
python src/main.py
```

### 4. Running Automated Tests
```powershell
python -m unittest discover tests
```

---

## 📦 Building Standalone Executable & Windows Installer

### Build Executable (`ApexLoad.exe`)
```powershell
pyinstaller ApexLoad.spec --noconfirm
```

### Build Windows Setup Installer
Compile `installer/installer.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php):
```powershell
iscc installer/installer.iss
```
This produces `dist/installer/ApexLoad-Setup-x64.exe` with Start Menu and Desktop shortcuts and full uninstaller registration.
