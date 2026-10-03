# ⚡ ytfetch

> **Modern, High-Performance YouTube Downloader & Media Converter for Windows**

**ytfetch** is a sleek, hardware-accelerated desktop application built with **PySide6 (Qt 6)**, **yt-dlp**, and **FFmpeg**. It pairs raw command-line extraction speed with an intuitive, non-blocking interface designed for smooth 60 FPS performance on Windows 10 and 11.

---

## ✨ Features

- 🎯 **Clean & Canonical Links**: Automatically strips tracking query params (`?si=`, `&feature=`, etc.).
- 📋 **Windows Clipboard Watcher**: Detects copied YouTube links and prompts with a one-click fetch banner.
- 🎬 **Multi-Format Video Downloads**: MP4, MKV, WebM in up to 4K (2160p), 1440p, 1080p 60fps, 720p, with dynamic size calculation.
- 🎵 **High-Fidelity Audio Extraction**: Convert videos into high-bitrate MP3 (320 kbps), Lossless FLAC, M4A, WAV, or OGG.
- 🎨 **Automatic Artwork & Metadata**: Embeds high-resolution cover art and populates Title, Artist/Channel, and Year into ID3/MP4 tags.
- 📑 **Playlist Inspector**: Browse full playlists with thumbnail previews, durations, search filtering, and selective batch downloading.
- ✂️ **Time Snipping & Chapters**: Download specific time ranges or split audio/video into separate tagged chapter tracks.
- 🚀 **Hardware-Accelerated Threaded Queue**: Asynchronous worker pool (`QThreadPool`) with live progress, transfer speed (MB/s), ETA timer, pause/resume, and cancellation.
- 🕒 **Download History**: Local SQLite history tracking with one-click "Open File" and "Open in Explorer" actions.
- 🌙 **Adaptive Dark & Light Modes**: Tailored dark slate aesthetic with vibrant accents and full high-contrast light mode.
- 🔄 **Non-Invasive Auto-Updates**: Quietly checks GitHub Releases for software updates and provides one-click update & restart.
- ⚙️ **Self-Managing Dependencies**: Auto-detects system and WinGet FFmpeg; one-click updater for the `yt-dlp` extraction engine.

---

## 🛠️ Project Structure

```
ytfetch/
├── .venv/                      # Python 3.11 virtual environment
├── .github/
│   └── workflows/
│       └── release.yml         # GitHub Actions automated release pipeline
├── installer/
│   ├── installer.iss           # Inno Setup Windows installer script
│   └── ytfetch.ico             # Application icon
├── src/
│   ├── main.py                 # Application entry point & Qt event loop
│   ├── core/
│   │   ├── config.py           # Configuration manager
│   │   ├── sanitizer.py        # URL cleaner & smart detector
│   │   ├── ffmpeg_mgr.py       # FFmpeg/FFprobe locator & fallback installer
│   │   ├── extractor.py        # yt-dlp metadata extraction & size calculator
│   │   ├── downloader.py       # Hardened download worker & progress hooks
│   │   ├── history.py          # SQLite history storage & shell launcher
│   │   ├── updater.py          # yt-dlp core updater
│   │   └── app_updater.py      # GitHub Releases auto-updater
│   ├── ui/
│   │   ├── theme.py            # Dark & Light QSS stylesheets
│   │   ├── main_window.py      # Main window & layout coordination
│   │   └── components/
│   │       ├── url_input_bar.py    # URL bar with clipboard toast
│   │       ├── preview_card.py     # Theme-adaptive video card
│   │       ├── options_panel.py    # Format, bitrate, resolution, snipping
│   │       ├── playlist_view.py    # Playlist table & bulk selection
│   │       ├── queue_widget.py     # Sleek download queue with mini-thumbs
│   │       ├── history_widget.py   # Download history table
│   │       ├── settings_dialog.py  # App settings & engine status
│   │       └── update_dialog.py    # In-app updater dialog with restart
│   └── assets/
│       └── ytfetch.ico         # App icon
├── tests/
│   ├── test_sanitizer.py       # URL cleaner tests
│   ├── test_history.py         # History & FFmpeg tests
│   └── test_updater.py         # Update checker tests
├── requirements.txt            # Python dependencies
├── ytfetch.spec                # PyInstaller build specification
└── README.md
```

---

## 🚀 Getting Started

### 1. Installation & Local Run
```powershell
# Navigate to project directory
cd h:\Dev\yt-download

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run application
python src/main.py
```

### 2. Running Automated Tests
```powershell
python -m unittest discover tests
```

---

## 📦 Packaging Standalone Executable & Installer

### Build Executable (`ytfetch.exe`)
```powershell
pyinstaller ytfetch.spec --noconfirm
```

### Build Windows Setup Installer
```powershell
iscc installer/installer.iss
```
Generates `dist/installer/ytfetch-Setup-x64.exe` with Start Menu and Desktop shortcuts.
