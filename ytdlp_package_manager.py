
from pathlib import Path
import zipfile
import re
import requests
import sys

_file_path: Path = Path(__file__)

# Directory containing the current Python file
_file_directory: Path = _file_path.parent

_current_zip_path: Path = _file_directory / "yt-dlp"

def get_current_zip_path():
    return _current_zip_path

def set_current_zip_path(new_zip_path: Path):
    current_zip_path = new_zip_path

YT_DLP_VERSION_REGEX = r"__version__\s*=\s*['\"]([^'\"]+)['\"]"

def parse_yt_dlp_version(version: str) -> tuple[int, ...]:
    return tuple(map(int, version.split(".")))

def get_yt_dlp_version_in_version_py(text: str) -> str | None:
    return re.search(
        YT_DLP_VERSION_REGEX,
        text,
    )

def get_current_yt_dlp_version() -> str | None:

    try:
        with zipfile.ZipFile(_current_zip_path, "r") as archive:
            with archive.open("yt_dlp/version.py") as version_file:

                text = version_file.read().decode("utf-8")

                match = get_yt_dlp_version_in_version_py(text)

                return match.group(1) if match else None

    except (
        FileNotFoundError,
        KeyError,
        zipfile.BadZipFile,
    ):
        return None

def get_latest_yt_dlp_version() -> str | None:

    try:

        response = requests.get(
            "https://raw.githubusercontent.com/yt-dlp/yt-dlp/master/yt_dlp/version.py",
            timeout=10,
        )

        response.raise_for_status()

        match = get_yt_dlp_version_in_version_py(response.text)

        return match.group(1) if match else None

    except requests.RequestException:
        return None

def download_yt_dlp() -> None:

    url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"

    response = requests.get(url, stream=True, timeout=30)

    response.raise_for_status()

    with open(_current_zip_path, "wb") as file:

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

def add_yt_dlp_to_sys_path() -> None:

    zip_path_str = str(_current_zip_path.resolve())

    if zip_path_str not in sys.path:
        sys.path.insert(0, zip_path_str)

def update_yt_dlp() -> None:

    try:
        current_version = get_current_yt_dlp_version()

        if current_version is None:
            download_yt_dlp()
            add_yt_dlp_to_sys_path()
            return

        latest_version = get_latest_yt_dlp_version()

        if latest_version is None:
            download_yt_dlp()
            add_yt_dlp_to_sys_path()
            return

        current = parse_yt_dlp_version(current_version)
        latest = parse_yt_dlp_version(latest_version)

        if current < latest:
            print("Current version is older than the latest version.\nInstalling latest version...")
            download_yt_dlp()
        elif current > latest:
            print("Current version is newer than the latest version.")
        else:
            print("yt-dlp is already up to date.")

        add_yt_dlp_to_sys_path()

    except Exception as e:
        print("Failed to update yt-dlp: ", e)
