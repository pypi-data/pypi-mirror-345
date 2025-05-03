# ytp_dl/config.py

import sys
import urllib.request
import zipfile
from pathlib import Path

__all__ = [
    "TMP_DIR", "CONNS", "SPLITS", "MIN_SPLIT",
    "MAX_WORKERS", "TIMEOUT", "ensure_aria2c",
]

TMP_DIR     = Path("tmp")
CONNS       = 16
SPLITS      = 16
MIN_SPLIT   = "1M"
MAX_WORKERS = 5
TIMEOUT     = 3

ARIA2C_VERSION = "1.36.0"
ARIA2C_URL = (
    f"https://github.com/aria2/aria2/releases/"
    f"download/release-{ARIA2C_VERSION}/aria2-{ARIA2C_VERSION}-win-64bit-build1.zip"
)
ARIA2C_BIN_DIR = Path(__file__).parent / "bin"
ARIA2C_EXE     = ARIA2C_BIN_DIR / "aria2c.exe"

def ensure_aria2c() -> Path:
    # non-Windows: assume on PATH
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
