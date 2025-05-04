#!/usr/bin/env python3
# ytp_dl/cli.py

import sys
import time
import argparse
import asyncio
import subprocess
import shutil
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests
import yt_dlp
from PIL import Image

from .config import (
    TMP_DIR, CONNS, SPLITS, MIN_SPLIT,
    MAX_WORKERS, TIMEOUT, ensure_aria2c, ensure_ffmpeg,
)

logger = logging.getLogger(__name__)

def run_stream(cmd: list[str], outfile_name: str | None = None) -> int:
    """
    Run a subprocess, streaming every stdout/stderr line
    prefixed with “[download]”, and at the end emit
    “[download_complete] <outfile_name>” if provided.
    Returns the process’s exit code.
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )
    assert proc.stdout
    for line in proc.stdout:
        text = line.rstrip()
        if not text:
            continue
        print(f"[download] {text}")
        sys.stdout.flush()
    proc.stdout.close()
    code = proc.wait()
    if outfile_name:
        print(f"[download_complete] {outfile_name}")
        sys.stdout.flush()
    return code

def parse_video_id(url: str) -> str | None:
    from urllib.parse import urlparse, parse_qs
    u = urlparse(url)
    if u.hostname == "youtu.be":
        return u.path.lstrip("/")
    return parse_qs(u.query).get("v", [None])[0]

def get_available_heights(vid: str, proxies: list[str]) -> list[int]:
    """
    Fetch available video heights, retrying with different proxies until success.
    """
    for proxy in proxies:
        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "proxy": proxy,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
            return sorted(
                f["height"]
                for f in info.get("formats", [])
                if isinstance(f.get("height"), int)
            )
        except Exception as e:
            print(f"Proxy {proxy} failed: {e}. Trying next...")
            time.sleep(2)  # Wait 2 seconds before trying the next proxy
    sys.exit("Error: All proxies failed to fetch metadata.")

def resize_image(image_path: Path, size=(640, 640)):
    try:
        with Image.open(image_path) as img:
            if img.mode in ("RGBA", "LA"):
                img = img.convert("RGB")
            w, h = img.size
            if w > h:
                left = (w - h) // 2
                img = img.crop((left, 0, left + h, h))
            elif h > w:
                top = (h - w) // 2
                img = img.crop((0, top, w, top + w))
            img = img.resize(size, Image.Resampling.LANCZOS)
            img.save(image_path, "JPEG", quality=95)
            logger.info(f"Resized cover to {size}: {image_path}")
    except Exception:
        logger.exception(f"Failed to resize image at {image_path}")

def head_ok(url: str) -> bool:
    try:
        return requests.head(url, allow_redirects=True, timeout=TIMEOUT).status_code == 200
    except Exception:
        return False

def parse_args():
    p = argparse.ArgumentParser(
        prog="ytp-dl",
        usage="ytp-dl -o OUTDIR -p PROXY [--audio] URL [HEIGHT]",
    )
    p.add_argument(
        "-o",
        "--output-dir",
        dest="outdir",
        required=True,
        help="Directory to save the final file into",
    )
    p.add_argument(
        "-p",
        "--proxy",
        dest="proxy",
        required=True,
        help="Comma‑separated proxy URIs",
    )
    p.add_argument(
        "-a",
        "--audio",
        action="store_true",
        help="Download audio-only MP3 with embedded cover art",
    )
    p.add_argument("url", help="YouTube URL")
    p.add_argument(
        "height",
        nargs="?",
        default="1080p",
        help="Desired video height (e.g. 1080p)",
    )
    return p.parse_args()

async def fetch_pair(vid: str, height: str, proxies: list[str]) -> dict:
    """
    Race one fetch per proxy until one succeeds, with a delay between attempts.
    """
    loop = asyncio.get_running_loop()
    exe = ThreadPoolExecutor(min(MAX_WORKERS, len(proxies)))
    future: asyncio.Future[dict] = loop.create_future()

    def schedule():
        if not future.done():
            loop.run_in_executor(exe, worker)

    def worker():
        proxy = proxies.pop(0)
        proxies.append(proxy)
        ydl_opts: dict = {
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        if proxy.startswith("socks"):
            ydl_opts["proxy"] = proxy
        else:
            ydl_opts["all-proxy"] = proxy

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
        except Exception:
            time.sleep(2)  # Wait 2 seconds before trying the next proxy
            return schedule()

        fmts = info.get("requested_formats") or info.get("formats") or []
        vids = [
            f
            for f in fmts
            if isinstance(f.get("height"), int) and f["height"] <= int(height)
        ]
        if not vids:
            time.sleep(2)
            return schedule()
        vfmt = max(vids, key=lambda f: f["height"])
        afmt = next((f for f in fmts if f.get("acodec", "") != "none"), None)
        if not afmt:
            time.sleep(2)
            return schedule()

        if head_ok(afmt["url"]) and head_ok(vfmt["url"]):
            if not future.done():
                loop.call_soon_threadsafe(
                    future.set_result,
                    {
                        "title": info.get("title", ""),
                        "duration": info.get("duration", 0),
                        "video_url": vfmt["url"],
                        "audio_url": afmt["url"],
                        "video_ext": vfmt.get("ext", "mp4").lower(),
                        "thumbnail": info.get("thumbnail"),
                    },
                )
        else:
            time.sleep(2)
            return schedule()

    for _ in range(min(MAX_WORKERS, len(proxies))):
        schedule()

    return await future

async def _amain():
    args = parse_args()
    vid = parse_video_id(args.url) or sys.exit("Error: could not parse video ID")
    h = args.height.rstrip("p")
    proxies = [p.strip() for p in args.proxy.split(",") if p.strip()]
    if not proxies:
        sys.exit("Error: no proxies provided via -p")

    heights = get_available_heights(vid, proxies)
    if not heights or int(h) > max(heights):
        sys.exit(f"Error: requested {h}p but only up to {max(heights)}p available")

    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir()

    aria2c = ensure_aria2c()
    ffmpeg = ensure_ffmpeg()

    try:
        pair = await fetch_pair(vid, h, proxies)
        safe = (
            "".join(c for c in pair["title"] if c.isalnum() or c.isspace())
            .strip()[:150]
            or f"media_{vid}"
        )
        outdir = Path(args.outdir).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)

        if args.audio:
            atmp = TMP_DIR / f"{vid}_audio.tmp"
            run_stream(
                [
                    str(aria2c),
                    "-x",
                    str(CONNS),
                    "-s",
                    str(SPLITS),
                    f"--min-split-size={MIN_SPLIT}",
                    "--file-allocation=none",
                    "--continue",
                    "--max-tries=1",
                    "--retry-wait=5",
                    "-o",
                    str(atmp),
                    pair["audio_url"],
                ],
                outfile_name=f"{safe}.mp3",
            )

            cover_args: list[str] = []
            thumb = pair.get("thumbnail")
            if thumb and head_ok(thumb):
                cover_path = TMP_DIR / "cover.jpg"
                resp = requests.get(thumb, timeout=TIMEOUT)
                resp.raise_for_status()
                cover_path.write_bytes(resp.content)
                resize_image(cover_path)
                cover_args = [
                    "-i",
                    str(cover_path),
                    "-map",
                    "1:v",
                    "-metadata:s:v",
                    "title=Cover",
                    "-metadata:s:v",
                    "comment=Cover (front)",
                ]

            mp3_out = outdir / f"{safe}.mp3"
            cmd = [str(ffmpeg), "-i", str(atmp)] + cover_args + [
                "-map",
                "0:a",
                "-c:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                "-y",
                str(mp3_out),
            ]
            run_stream(cmd, outfile_name=mp3_out.name)
            return

        ext = "mkv" if pair["video_ext"] in ("webm", "mkv") else "mp4"
        vtmp = TMP_DIR / f"{vid}_video.{pair['video_ext']}"
        atmp = TMP_DIR / f"{vid}_audio.tmp"

        await asyncio.gather(
            asyncio.to_thread(
                run_stream,
                [
                    str(aria2c),
                    "-x",
                    str(CONNS),
                    "-s",
                    str(SPLITS),
                    f"--min-split-size={MIN_SPLIT}",
                    "--file-allocation=none",
                    "--continue",
                    "--max-tries=1",
                    "--retry-wait=5",
                    "-o",
                    str(vtmp),
                    pair["video_url"],
                ],
                vtmp.name,
            ),
            asyncio.to_thread(
                run_stream,
                [
                    str(aria2c),
                    "-x",
                    str(CONNS),
                    "-s",
                    str(SPLITS),
                    f"--min-split-size={MIN_SPLIT}",
                    "--file-allocation=none",
                    "--continue",
                    "--max-tries=1",
                    "--retry-wait=5",
                    "-o",
                    str(atmp),
                    pair["audio_url"],
                ],
                atmp.name,
            ),
        )

        final = outdir / f"{safe}.{ext}"
        run_stream(
            [str(ffmpeg), "-i", str(vtmp), "-i", str(atmp), "-c", "copy", "-y", str(final)],
            outfile_name=final.name,
        )

    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during download/merge: {e}")

    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)

def main():
    asyncio.run(_amain())

if __name__ == "__main__":
    main()