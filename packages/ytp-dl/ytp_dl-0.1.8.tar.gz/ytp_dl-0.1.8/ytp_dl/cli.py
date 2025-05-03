#!/usr/bin/env python3
# ytp_dl/cli.py

import sys
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


def parse_video_id(url: str) -> str | None:
    from urllib.parse import urlparse, parse_qs
    u = urlparse(url)
    if u.hostname == "youtu.be":
        return u.path.lstrip("/")
    return parse_qs(u.query).get("v", [None])[0]


def get_available_heights(vid: str) -> list[int]:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
    return sorted(
        f["height"] for f in info.get("formats", [])
        if isinstance(f.get("height"), int)
    )


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
        usage="ytp-dl -o OUTDIR -p PROXY [--audio] URL [HEIGHT]"
    )
    p.add_argument("-o", "--output-dir", dest="outdir", required=True,
                   help="Directory to save the final file into")
    p.add_argument("-p", "--proxy", dest="proxy", required=True,
                   help="Comma‑separated proxy URIs")
    p.add_argument("-a", "--audio", action="store_true",
                   help="Download audio-only MP3 with embedded cover art")
    p.add_argument("url", help="YouTube URL")
    p.add_argument("height", nargs="?", default="1080p",
                   help="Desired video height (e.g. 1080p)")
    return p.parse_args()


async def fetch_pair(vid: str, height: str, proxies: list[str]) -> dict:
    loop = asyncio.get_running_loop()
    exe = ThreadPoolExecutor(min(MAX_WORKERS, len(proxies)))
    future = loop.create_future()

    def schedule():
        if not future.done():
            loop.run_in_executor(exe, worker)

    def worker():
        proxy = proxies.pop(0); proxies.append(proxy)
        ydl_opts = {
            "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
            "quiet": True, "no_warnings": True, "noplaylist": True,
        }
        if proxy.startswith("socks"):
            ydl_opts["proxy"] = proxy
        else:
            ydl_opts["all-proxy"] = proxy

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
        except Exception:
            return schedule()

        fmts = info.get("requested_formats") or info.get("formats", [])
        vids = [f for f in fmts if isinstance(f.get("height"), int) and f["height"] <= int(height)]
        if not vids:
            return schedule()
        vfmt = max(vids, key=lambda f: f["height"])
        afmt = next((f for f in fmts if f.get("acodec", "") != "none"), None)
        if not afmt:
            return schedule()

        if head_ok(afmt["url"]) and head_ok(vfmt["url"]):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, {
                    "title":      info.get("title", ""),
                    "duration":   info.get("duration", 0),
                    "video_url":  vfmt["url"],
                    "audio_url":  afmt["url"],
                    "video_ext":  vfmt.get("ext", "mp4").lower(),
                    "thumbnail":  info.get("thumbnail"),
                })
        else:
            schedule()

    for _ in range(min(MAX_WORKERS, len(proxies))):
        schedule()

    return await future


async def _amain():
    args = parse_args()
    vid = parse_video_id(args.url) or sys.exit("Error: could not parse video ID")
    h = args.height.rstrip("p")
    heights = get_available_heights(vid)
    if not heights or int(h) > max(heights):
        sys.exit(f"Error: requested {h}p but only up to {max(heights)}p available")

    proxies = [p.strip() for p in args.proxy.split(",") if p.strip()]
    if not proxies:
        sys.exit("Error: no proxies provided via -p")

    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir()

    aria2c_bin = ensure_aria2c()
    ffmpeg_bin = ensure_ffmpeg()

    try:
        pair = await fetch_pair(vid, h, proxies)

        safe = "".join(c for c in pair["title"] if c.isalnum() or c.isspace()).strip()[:150] or f"media_{vid}"
        outdir = Path(args.outdir).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)

        # ─── Audio‑Only Mode ────────────────────
        if args.audio:
            atmp = TMP_DIR / f"{vid}_audio.tmp"
            subprocess.run([
                str(aria2c_bin), "-x", str(CONNS), "-s", str(SPLITS),
                f"--min-split-size={MIN_SPLIT}", "--file-allocation=none",
                "--continue", "--max-tries=1", "--retry-wait=5",
                "-o", str(atmp), pair["audio_url"]
            ], check=True)

            # cover
            cover = None
            thumb_url = pair.get("thumbnail")
            if thumb_url and head_ok(thumb_url):
                cover = TMP_DIR / "cover.jpg"
                resp = requests.get(thumb_url, timeout=TIMEOUT)
                resp.raise_for_status()
                cover.write_bytes(resp.content)
                resize_image(cover)

            out_mp3 = outdir / f"{safe}.mp3"
            cmd = [str(ffmpeg_bin), "-i", str(atmp)]
            if cover:
                cmd += ["-i", str(cover)]
            cmd += ["-map", "0:a"]
            if cover:
                cmd += ["-map", "1:v", "-metadata:s:v", "title=Cover", "-metadata:s:v", "comment=Cover (front)"]
            cmd += ["-c:a", "libmp3lame", "-qscale:a", "2", "-y", str(out_mp3)]

            subprocess.run(cmd, check=True)
            print(f"✅ Saved audio to {out_mp3}")
            return

        # ─── Video Mode ────────────────────────
        ext = "mkv" if pair["video_ext"] in ("webm", "mkv") else "mp4"
        out = outdir / f"{safe}.{ext}"

        vtmp = TMP_DIR / f"{vid}_video.{pair['video_ext']}"
        atmp = TMP_DIR / f"{vid}_audio.tmp"

        await asyncio.gather(
            asyncio.to_thread(subprocess.run, [
                str(aria2c_bin), "-x", str(CONNS), "-s", str(SPLITS),
                f"--min-split-size={MIN_SPLIT}", "--file-allocation=none",
                "--continue", "--max-tries=1", "--retry-wait=5",
                "-o", str(vtmp), pair["video_url"]
            ], check=True),
            asyncio.to_thread(subprocess.run, [
                str(aria2c_bin), "-x", str(CONNS), "-s", str(SPLITS),
                f"--min-split-size={MIN_SPLIT}", "--file-allocation=none",
                "--continue", "--max-tries=1", "--retry-wait=5",
                "-o", str(atmp), pair["audio_url"]
            ], check=True),
        )

        subprocess.run([
            str(ffmpeg_bin), "-i", str(vtmp), "-i", str(atmp),
            "-c", "copy", "-y", str(out)
        ], check=True)
        print(f"✅ Saved video to {out}")

    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during download/merge: {e}")

    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)


def main():
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
