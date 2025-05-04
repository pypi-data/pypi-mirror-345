# 🎵 ytp2mp3

[![PyPI version](https://badge.fury.io/py/ytp2mp3.svg)](https://pypi.org/project/ytp2mp3/)

**ytp2mp3** is a Python-based command-line tool that downloads a YouTube playlist and merges all audio tracks into a single `.mp3` file.

Enjoy listening to your favorite playlists as one contiguous audio file, and skip advertisements. 

---

## 🚀 Features

- Downloads entire **YouTube playlists**
- Extracts **audio only**
- Merges all tracks into one `.mp3` file
- Cross-platform (Windows, macOS, Linux)
- Built with `yt-dlp`, `pydub`, and `ffmpeg`

---

## 📦 Installation

Installation of Python is required.  You can install the tool from [PyPI](https://pypi.org/project/ytp2mp3/)

```bash
pip install ytp2mp3
```

⚠️ ffmpeg is required — see below.

## Usage

| Option             | Description                                              |
| ------------------ | -------------------------------------------------------- |
| `url` (positional) | The YouTube playlist URL                                 |
| `-o`, `--output`   | Name of the output `.mp3` file (default: `combined.mp3`) |

## 🔧 System Requirement: ffmpeg

pydub requires ffmpeg to process audio streams.

### macOS
```bash
brew install ffmpeg
```

### Ubuntu / Debian
```bash
sudo apt install ffmpeg
```

### Windows
Download from ffmpeg.org

Add the bin/ folder to your system PATH

