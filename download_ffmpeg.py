#!/usr/bin/env python3
"""
Download FFmpeg binaries for different platforms and architectures.
Uses videohelp.com downloads for FFmpeg binaries.
"""

import os
import sys
import zipfile
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlretrieve


def download_file(url, dest_path):
    """Download a file from URL to destination path."""
    if os.path.exists(dest_path):
        print(f"Already exists: {dest_path}, skipping download")
        return
    print(f"Downloading: {url}")
    urlretrieve(url, dest_path)
    print(f"Downloaded to: {dest_path}")


def extract_zip(zip_path, extract_dir):
    """Extract zip archive."""
    print(f"Extracting: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)


def extract_7z(archive_path, extract_dir):
    """Extract 7z archive using 7z command."""
    print(f"Extracting: {archive_path}")
    # Try to use 7z command (available on macOS via brew install p7zip, Windows via 7-Zip)
    try:
        subprocess.run(["7z", "x", str(archive_path), f"-o{extract_dir}", "-y"], check=True)
    except FileNotFoundError:
        # Try 7za (alternative name)
        try:
            subprocess.run(["7za", "x", str(archive_path), f"-o{extract_dir}", "-y"], check=True)
        except FileNotFoundError:
            print("ERROR: 7z or 7za command not found. Please install p7zip or 7-Zip.")
            sys.exit(1)


def find_ffmpeg_binary(directory, filename_patterns):
    """Find FFmpeg binary in directory tree."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            for pattern in filename_patterns:
                if pattern in file:
                    # For Windows, look for .exe
                    if pattern.endswith('.exe') and file.endswith('.exe'):
                        return os.path.join(root, file)
                    # For macOS/Linux, look for ffmpeg without extension
                    elif not pattern.endswith('.exe') and pattern in file:
                        # Make sure it's the actual ffmpeg binary, not a .txt or other file
                        if file == 'ffmpeg' or (file.startswith('ffmpeg') and '.' not in file):
                            return os.path.join(root, file)
    return None


def main():
    output_dir = Path(".")
    temp_dir = Path("temp_download")
    temp_dir.mkdir(exist_ok=True)

    releases = [
        {
            "name": "ffmpeg-win-x64.exe",
            "url": "https://www.videohelp.com/download/ffmpeg-8.0.1-full_build.7z?r=NqfVcTvLBJ",
            "type": "7z",
            "patterns": ["ffmpeg.exe"],
        },
        {
            "name": "ffmpeg-darwin-x64",
            "url": "https://www.videohelp.com/download/ffmpeg-8.0.1-macos64-static.7z?r=NqfVcTvLBJ",
            "type": "7z",
            "patterns": ["ffmpeg"],
        },
        {
            "name": "ffmpeg-darwin-arm64",
            "url": "https://www.videohelp.com/download/ffmpeg-8.0-macosarm-static.zip?r=NqfVcTvLBJ",
            "type": "zip",
            "patterns": ["ffmpeg"],
        },
    ]

    for release in releases:
        print(f"\n{'='*50}")
        print(f"Processing: {release['name']}")
        print(f"{'='*50}")

        archive_ext = release["type"]  # "zip" or "7z"
        archive_name = release["name"] + f".{archive_ext}"
        archive_path = temp_dir / archive_name
        extract_dir = temp_dir / f"extract_{release['name']}"

        # Download
        download_file(release["url"], archive_path)

        # Extract
        extract_dir.mkdir(exist_ok=True)
        if release["type"] == "zip":
            extract_zip(archive_path, extract_dir)
        else:
            extract_7z(archive_path, extract_dir)

        # Find FFmpeg binary
        ffmpeg_binary = find_ffmpeg_binary(extract_dir, release["patterns"])

        if ffmpeg_binary:
            print(f"Found FFmpeg binary: {ffmpeg_binary}")

            # Copy to output with new name
            dest_path = output_dir / release["name"]
            shutil.copy2(ffmpeg_binary, dest_path)
            print(f"Copied to: {dest_path}")

            # Make executable on macOS/Linux
            if not release["name"].endswith(".exe"):
                os.chmod(dest_path, 0o755)
                print(f"Made executable: {dest_path}")
        else:
            print(f"ERROR: Could not find FFmpeg binary in {extract_dir}")
            # List files for debugging
            print("Files in extract directory:")
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    print(f"  {os.path.join(root, file)}")
            sys.exit(1)

        # Cleanup
        os.remove(archive_path)
        shutil.rmtree(extract_dir)

    print("\n" + "="*50)
    print("All FFmpeg binaries downloaded successfully!")
    print("="*50)


if __name__ == "__main__":
    main()
