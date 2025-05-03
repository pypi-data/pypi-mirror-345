#!/usr/bin/env python3
# ytp_dl/url_scrape.py

import sys
import json
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--proxy", default=__import__("os").environ.get("YTPDL_PROXY",""))
    p.add_argument("video_id", help="YouTube video ID")
    p.add_argument("height",   help="Desired height (e.g. 1080)")
    return p.parse_args()


def extract_one(proxy_uri, vid, height):
    ydl_opts = {
        "format": f"bestvideo[height<={height}]+bestaudio/best[height<={height}]",
        "quiet": True, "no_warnings": True, "noplaylist": True,
    }
    if proxy_uri.startswith("socks"):
        ydl_opts["proxy"] = proxy_uri
    else:
        ydl_opts["all-proxy"] = proxy_uri

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://youtu.be/{vid}", download=False)
    except:
        return None

    fmts = info.get("requested_formats") or info.get("formats", [])
    vids = [f for f in fmts if isinstance(f.get("height"), int) and f["height"] <= int(height)]
    if not vids:
        return None
    vfmt = max(vids, key=lambda f: f["height"])
    afmt = next((f for f in fmts if f.get("acodec","") != "none"), None)
    if not afmt:
        return None

    return {
        "title":     info.get("title",""),
        "duration":  info.get("duration",0),
        "video_url": vfmt["url"],
        "audio_url": afmt["url"],
    }


def main():
    args = parse_args()
    proxies = [u.strip() for u in args.proxy.split(",") if u.strip()]
    if not proxies:
        sys.exit("Error: no proxy URIs provided (via --proxy or YTPDL_PROXY)")

    with ThreadPoolExecutor(max_workers=len(proxies)) as pool:
        futures = { pool.submit(extract_one, p, args.video_id, args.height): p for p in proxies }
        for fut in as_completed(futures):
            res = fut.result()
            if res:
                pool.shutdown(cancel_futures=True)
                print(json.dumps(res))
                sys.exit(0)

    sys.exit("Error: Failed to fetch any valid URL pair")


if __name__ == "__main__":
    main()
