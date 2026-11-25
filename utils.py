
from Paths import Paths

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tkinter as tk
from tkinter import ttk
from urllib.parse import urlsplit
import ipaddress
import re
import requests

@dataclass
class ValidateBinaryResult:
    isInstalled: bool
    isWorking: bool

@dataclass
class ValidateBinariesResult:

    ffmpeg: ValidateBinaryResult
    ffprobe: ValidateBinaryResult
    qjs: ValidateBinaryResult

    def isWorking(self) -> bool:
        return (
            self.ffmpeg.isWorking
            and self.ffprobe.isWorking
            and self.qjs.isWorking
        )

    def errorMessage(self) -> str | None:

        if self.isWorking():
            return None

        return (
            "ffmpeg:" + "\n"
            "Is installed: " + ("Yes" if self.ffmpeg.isInstalled else "No") + "\n"
            "Is Working: " + ("Yes" if self.ffmpeg.isWorking else "No") + "\n"
            "\n"
            "ffprobe:" + "\n"
            "Is installed: " + ("Yes" if self.ffprobe.isInstalled else "No") + "\n"
            "Is Working: " + ("Yes" if self.ffprobe.isWorking else "No") + "\n"
            "\n"
            "qjs:" + "\n"
            "Is installed: " + ("Yes" if self.qjs.isInstalled else "No") + "\n"
            "Is Working: " + ("Yes" if self.qjs.isWorking else "No") + "\n"
        )

def validateBinaries() -> ValidateBinariesResult:

    def _validateExecutable(
        path: Path,
        arguements: list[str],
        expectedReturnCode: int
    ) -> ValidateBinaryResult:

        print(f"\nLooking for executable at '{str(path)}'...")

        isInstalled: bool = path.is_file()

        toolName: str = path.name

        if not isInstalled:
            print(f"Missing executable: '{toolName}.'")
            return ValidateBinaryResult(
                isInstalled=False,
                isWorking=False
            )

        print(f"Found executable '{toolName}'.")

        try:
            result = subprocess.run(
                args=[str(path), *arguements,],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            isWorking: bool = result.returncode == expectedReturnCode

            if isWorking:
                helpOutput = (
                    result.stdout.strip()
                    or result.stderr.strip()
                )
                print(f"Executable working.")
            else:
                print(
                    f"Executable failed with exit code {result.returncode}:\n"
                    f"{result.stderr.strip()}."
                )

            return ValidateBinaryResult(
                isInstalled=isInstalled,
                isWorking=isWorking
            )

        except subprocess.TimeoutExpired:
            print(f"Executable timed out: '{toolName}'")

        except OSError as e:
            print(f"Failed to execute '{toolName}': {e}")

        return ValidateBinaryResult(
            isInstalled=True,
            isWorking=False
        )

    ffmpegResult: ValidateBinaryResult = _validateExecutable(
        path=Paths.ffmpeg(),
        arguements=["-version"],
        expectedReturnCode=0
    )

    ffprobeResult: ValidateBinaryResult = _validateExecutable(
        path=Paths.ffprobe(),
        arguements=["-version"],
        expectedReturnCode=0
    )

    qjsResult: ValidateBinaryResult = _validateExecutable(
        path=Paths.qjs(),
        arguements=["--eval", "console.log('QuickJS is working!')"],
        expectedReturnCode=0
    )

    print()

    return ValidateBinariesResult(
        ffmpeg=ffmpegResult,
        ffprobe=ffprobeResult,
        qjs=qjsResult
    )

def setWidgetState(
    widget: tk.Widget,
    enabled: bool
) -> None:

    try:
        if isinstance(widget, ttk.Combobox):
            widget.configure(
                state="readonly" if enabled else "disabled"
            )
        elif isinstance(widget, (ttk.Entry, ttk.Checkbutton, ttk.Button)):
            widget.configure(
                state="normal" if enabled else "disabled"
            )
    except tk.TclError:
        pass

    for childWidget in widget.winfo_children():
        setWidgetState(
            widget=childWidget,
            enabled=enabled
        )

def isValidUrl(url: str) -> bool:

    url = url.strip()

    if not url:
        return False

    # Reject whitespace and control characters.
    if any(character.isspace() or ord(character) < 32 for character in url):
        return False

    try:
        parsedUrl = urlsplit(url)

        # Only accept web URLs.
        if parsedUrl.scheme.lower() not in ("http", "https"):
            return False

        # A hostname is required.
        hostname = parsedUrl.hostname

        if not hostname:
            return False

        # Reject URLs containing credentials.
        if parsedUrl.username is not None or parsedUrl.password is not None:
            return False

        # Accessing .port raises ValueError for invalid ports.
        port = parsedUrl.port

        if port is not None and not (1 <= port <= 65535):
            return False

        # Validate IP addresses, including IPv6.
        try:
            ipaddress.ip_address(hostname)
            return True
        except ValueError:
            pass

        # Validate domain names.
        hostname = hostname.encode("idna").decode("ascii")

        if len(hostname) > 253:
            return False

        labels = hostname.rstrip(".").split(".")

        if len(labels) < 2:
            return False

        for label in labels:
            if not label or len(label) > 63:
                return False

            if not re.fullmatch(
                r"[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?",
                label
            ):
                return False

        return True

    except (ValueError, UnicodeError):
        return False

@dataclass
class YoutubeVideoMetadata:
    title: str
    author_name: str
    author_url: str
    type: str
    height: int
    width: int
    version: str
    provider_name: str
    provider_url: str
    thumbnail_height: int
    thumbnail_width: int
    thumbnail_url: str

def getYoutubeVideoMetadata(youtubeVideoLink: str) -> YoutubeVideoMetadata | None:

    if not isValidUrl(youtubeVideoLink):
        print("Url is invalid, returning None")
        return None

    if not any(domain in youtubeVideoLink for domain in (
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "youtu.be"
    )):
        print("URL is not a YouTube video URL, returning None")
        return None

    try:
        response = requests.get(
            "https://www.youtube.com/oembed",
            params={
                "url": youtubeVideoLink,
                "format": "json"
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return YoutubeVideoMetadata(
            title=data["title"],
            author_name=data["author_name"],
            author_url=data["author_url"],
            type=data["type"],
            height=data["height"],
            width=data["width"],
            version=data["version"],
            provider_name=data["provider_name"],
            provider_url=data["provider_url"],
            thumbnail_height=data["thumbnail_height"],
            thumbnail_width=data["thumbnail_width"],
            thumbnail_url=data["thumbnail_url"]
        )

    except requests.exceptions.RequestException:
        print("An error occured while requesting metadata, returning None")
        return None
