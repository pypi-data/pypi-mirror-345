import sys
import urllib.request
import zipfile
from pathlib import Path

__all__ = [
    "TMP_DIR", "CONNS", "SPLITS", "MIN_SPLIT",
    "MAX_WORKERS", "TIMEOUT", "ensure_aria2c", "ensure_ffmpeg",
]

TMP_DIR     = Path("tmp")
CONNS       = 4  # Reduced from 16 to avoid overwhelming the server
SPLITS      = 4  # Reduced from 16 for the same reason
MIN_SPLIT   = "1M"
MAX_WORKERS = 5
TIMEOUT     = 3

# ─── aria2c installer ───────────────────────────
ARIA2C_VERSION = "1.36.0"
ARIA2C_URL = (
    f"https://github.com/aria2/aria2/releases/"
    f"download/release-{ARIA2C_VERSION}/aria2-{ARIA2C_VERSION}-win-64bit-build1.zip"
)
ARIA2C_BIN_DIR = Path(__file__).parent / "bin"
ARIA2C_EXE     = ARIA2C_BIN_DIR / "aria2c.exe"

def ensure_aria2c() -> Path:
    if sys.platform != "win32":
        return Path("aria2c")
    if ARIA2C_EXE.exists():
        return ARIA2C_EXE

    ARIA2C_BIN_DIR.mkdir(exist_ok=True)
    zip_path = ARIA2C_BIN_DIR / f"aria2-{ARIA2C_VERSION}.zip"

    print("🔽 Downloading aria2c…")
    urllib.request.urlretrieve(ARIA2C_URL, zip_path)

    print("📦 Extracting aria2c.exe…")
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            if member.endswith("aria2c.exe"):
                z.extract(member, ARIA2C_BIN_DIR)
                (ARIA2C_BIN_DIR / member).rename(ARIA2C_EXE)
                break

    zip_path.unlink()
    print("✅ aria2c ready.")
    return ARIA2C_EXE

# ─── ffmpeg installer ────────────────────────────
FFMPEG_VERSION = "6.0"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_BIN_DIR = Path(__file__).parent / "bin"
FFMPEG_EXE = FFMPEG_BIN_DIR / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")

def ensure_ffmpeg() -> Path:
    # Non-Windows: assume ffmpeg is on PATH
    if sys.platform != "win32":
        return Path("ffmpeg")

    if FFMPEG_EXE.exists():
        return FFMPEG_EXE

    FFMPEG_BIN_DIR.mkdir(exist_ok=True)
    zip_path = FFMPEG_BIN_DIR / f"ffmpeg-{FFMPEG_VERSION}.zip"

    print("🔽 Downloading ffmpeg…")
    urllib.request.urlretrieve(FFMPEG_URL, zip_path)

    print("📦 Extracting ffmpeg.exe…")
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            if member.endswith("ffmpeg.exe"):
                z.extract(member, FFMPEG_BIN_DIR)
                (FFMPEG_BIN_DIR / member).rename(FFMPEG_EXE)
                break

    zip_path.unlink()
    print("✅ ffmpeg ready.")
    return FFMPEG_EXE