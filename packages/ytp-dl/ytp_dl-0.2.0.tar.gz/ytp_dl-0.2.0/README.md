# ytp-dl

A YouTube downloader built on top of `yt-dlp` that bypasses YouTube throttling. It uses proxies to fetch signed DASH URLs, then downloads video and audio segments in parallel with `aria2c`, and merges them with `ffmpeg` into a single output file.

## 📦 Installation

```bash
pip install ytp-dl
```

## ▶️ Basic Usage

```bash
ytp-dl -o /path/to/save -p <proxy1,proxy2,…> 'https://youtu.be/VIDEO_ID' [HEIGHT]
```

- `-o`: Directory to save the final video.
- `-p`: Comma-separated proxy list (used to fetch signed media URLs).
- `HEIGHT` (optional): Target resolution (e.g., `720p`, default: `1080p`).

### Example:

```bash
ytp-dl -o ~/Videos -p socks5://127.0.0.1:9050,https://myproxy.com 'https://youtu.be/dQw4w9WgXcQ' 720p
```

---

## 🎵 Audio-Only Mode

Download just the audio as MP3 with embedded cover art:

### Example:

```bash
ytp-dl -a -o ~/Music -p socks5://127.0.0.1:9050,https://myproxy.com 'https://youtu.be/dQw4w9WgXcQ'
```

- Downloads the best available audio stream
- Embeds the thumbnail as cover art
- Saves output as `<title>.mp3` in the specified folder

---

## ⚙️ Dependencies

Make sure the following are available in your system PATH or bundled locally:

- [`aria2c`](https://aria2.github.io/)
- [`ffmpeg`](https://ffmpeg.org/)
- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp)

These are handled automatically in most usage cases.