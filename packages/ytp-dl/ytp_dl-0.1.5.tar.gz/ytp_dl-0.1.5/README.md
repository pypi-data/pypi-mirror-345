ytp-dl

A YouTube downloader built on top of yt-dlp that bypasses YouTube throttling. It uses proxies to fetch signed DASH URLs, then downloads video and audio segments in parallel with aria2c and merges them with ffmpeg into a single MP4 file.

Installation

pip install ytp-dl

Basic Usage

ytp-dl -o /path/to/save -p <proxy1,proxy2,…> https://youtu.be/VIDEO_ID [HEIGHT]

-o: Directory where the final video will be saved.

-p: Comma-separated list of proxy URIs (used only for URL signing).

https://youtu.be/VIDEO_ID: The YouTube video URL.

[HEIGHT] (optional): Desired resolution (e.g., 720p, defaults to 1080p).

That’s it—proxies are used just to get valid URLs, aria2c downloads segments directly, and ffmpeg handles merging.