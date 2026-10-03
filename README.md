# ytfetch

A simple desktop app to download YouTube videos and audio quickly, without having to use ad-ridden web downloaders.

Built with Python (PySide6), yt-dlp, and FFmpeg.

---

## What it does

- Download YouTube videos in MP4, MKV, or WebM up to available resolutions (1080p, 4K).
- Extract audio to MP3, M4A, or FLAC with cover art and tags embedded.
- Download full playlists or pick specific tracks with the built-in inspector.
- Automatically creates a folder for playlists if you want to keep them organized.
- Active queue with progress, speed, and cancel options.
- History log to open downloaded files or reveal them in Explorer.
- Dark and light mode toggle.
- Uses existing FFmpeg on your system (or downloads a portable copy if you don't have it).

---

## Running from Source

### Prerequisites
- Python 3.11+
- FFmpeg (optional, recommended via `winget install Gyan.FFmpeg`)

### Setup
```powershell
# Clone the repository
git clone https://github.com/TOXiC-G/ytfetch.git
cd ytfetch

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run the app
python src/main.py
```

---

## Building the Executable

To compile into a standalone `.exe`:

```powershell
pyinstaller ytfetch.spec --noconfirm
```

The executable will be generated at `dist/ytfetch.exe`.
