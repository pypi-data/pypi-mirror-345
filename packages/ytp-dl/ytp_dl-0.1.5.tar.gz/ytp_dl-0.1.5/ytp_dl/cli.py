#!/usr/bin/env python3
# ytp_dl/cli.py

import sys
import argparse
import asyncio
import subprocess
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import requests
import yt_dlp

from .config import (
    TMP_DIR, CONNS, SPLITS, MIN_SPLIT,
    MAX_WORKERS, TIMEOUT, ensure_aria2c,
)

def parse_args():
    p = argparse.ArgumentParser(
        prog="ytp-dl",
        usage="ytp-dl -o OUTDIR -p PROXY URL [HEIGHT]"
    )
    p.add_argument("-o", "--output-dir", dest="outdir", required=True,
                   help="Directory to save the final .mp4 into")
    p.add_argument("-p", "--proxy", dest="proxy", required=True,
                   help="Comma‑separated proxy URIs")
    p.add_argument("url", help="YouTube URL")
    p.add_argument("height", nargs="?", default="1080p",
                   help="Desired video height (e.g. 1080p)")
    return p.parse_args()

def parse_video_id(url):
    from urllib.parse import urlparse, parse_qs
    u = urlparse(url)
    if u.hostname == "youtu.be":
        return u.path.lstrip("/")
    return parse_qs(u.query).get("v", [None])[0]

def get_available_heights(vid):
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
    return sorted(
        f["height"] for f in info.get("formats", [])
        if f.get("vcodec") and isinstance(f.get("height"), int)
    )

def head_ok(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code == 200
    except:
        return False

async def fetch_pair(vid, height, proxies):
    loop   = asyncio.get_running_loop()
    exe    = ThreadPoolExecutor(min(MAX_WORKERS, len(proxies)))
    future = loop.create_future()

    def schedule():
        if not future.done():
            loop.run_in_executor(exe, worker)

    def worker():
        proxy = proxies.pop(0); proxies.append(proxy)
        ydl_opts = {
            "format": f"bestvideo[height={height}][vcodec^=avc1]+bestaudio",
            "quiet": True, "no_warnings": True, "noplaylist": True
        }
        if proxy.startswith("socks"):
            ydl_opts["proxy"] = proxy
        else:
            ydl_opts["all-proxy"] = proxy

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
        except:
            return schedule()

        fmts = info.get("requested_formats") or info.get("formats", [])
        vfmt = next(
            (f for f in fmts
             if f.get("vcodec","").startswith("avc1")
             and f.get("ext","").lower() in ("mp4","m4v")),
            None
        )
        afmt = next((f for f in fmts if f.get("acodec","")!="none"), None)
        if not vfmt or not afmt:
            return schedule()

        if head_ok(vfmt["url"]) and head_ok(afmt["url"]):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, {
                    "title":     info.get("title",""),
                    "duration":  info.get("duration",0),
                    "video_url": vfmt["url"],
                    "audio_url": afmt["url"],
                })
        else:
            schedule()

    for _ in range(min(MAX_WORKERS, len(proxies))):
        schedule()

    return await future

async def _amain():
    args    = parse_args()
    vid     = parse_video_id(args.url)
    if not vid:
        sys.exit("Error: could not parse video ID")

    h       = args.height.rstrip("p")
    heights = get_available_heights(vid)
    if not heights or int(h) > max(heights):
        sys.exit(f"Error: requested {h}p but only up to {max(heights or [0])}p available")

    proxies = [p.strip() for p in args.proxy.split(",") if p.strip()]
    if not proxies:
        sys.exit("Error: no proxies provided via -p")

    # prepare tmp directory
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir()

    # ensure aria2c is installed or on PATH
    aria2c_bin = ensure_aria2c()

    try:
        pair = await fetch_pair(vid, h, proxies)

        safe   = "".join(c for c in pair["title"]
                         if c.isalnum() or c.isspace()).strip()[:150] \
                 or f"video_{vid}"
        outdir = Path(args.outdir).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)
        out    = outdir / f"{safe}.mp4"
        vtmp   = TMP_DIR / f"{vid}_video.tmp"
        atmp   = TMP_DIR / f"{vid}_audio.tmp"

        # parallel downloads
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

        # merge
        subprocess.run(
            ["ffmpeg", "-i", str(vtmp), "-i", str(atmp),
             "-c", "copy", "-y", str(out)],
            check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
        )

    except subprocess.CalledProcessError as e:
        sys.exit(f"Error during download/merge: {e}")
    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)

def main():
    # synchronous entry point for setuptools console_scripts
    asyncio.run(_amain())

if __name__ == "__main__":
    main()
