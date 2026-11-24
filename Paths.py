
import platform
from pathlib import Path

class Paths:

    @staticmethod
    def _executableFileExtension() -> str:
        system: str = platform.system()
        match system:
            case "Windows":
                return ".exe"
            case "Linux" | "Darwin":
                return ""
            case _:
                raise OSError(f"Unsupported platform: '{system}'")

    @staticmethod
    def _platformName() -> str:
        system: str = platform.system()
        match system:
            case "Windows":
                return "windows"
            case "Linux":
                return "linux"
            case "Darwin":
                return "macos"
            case _:
                raise OSError(f"Unsupported platform: '{system}'")

    @staticmethod
    def scriptDir() -> Path:
        return Path(__file__).resolve().parent

    @staticmethod
    def binDir() -> Path:
        return Paths.scriptDir() / "bin"

    @staticmethod
    def currentPlatformBinDir() -> Path:
        return Paths.binDir() / Paths._platformName()

    @staticmethod
    def ffmpeg() -> Path:
        return Paths.currentPlatformBinDir() / f"ffmpeg{Paths._executableFileExtension()}"

    @staticmethod
    def ffprobe() -> Path:
        return Paths.currentPlatformBinDir() / f"ffprobe{Paths._executableFileExtension()}"

    @staticmethod
    def qjs() -> Path:
        return Paths.currentPlatformBinDir() / f"qjs{Paths._executableFileExtension()}"

    @staticmethod
    def yt_dlp_cache_dir() -> Path:
        directory = Paths.scriptDir() / "cache" / "yt-dlp"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
