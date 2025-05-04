from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ytp-dl",
    version="0.2.41",
    description="Proxy‑based yt-dlp downloader with aria2c+ffmpeg support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="dumgum82",
    author_email="dumgum42@gmail.com",
    packages=find_packages(include=["ytp_dl", "ytp_dl.*"]),
    install_requires=[
        "yt-dlp",
        "requests",
        "Pillow",
    ],
    entry_points={
        "console_scripts": [
            "ytp-dl = ytp_dl.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
