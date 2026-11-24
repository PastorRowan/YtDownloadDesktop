
from Paths import Paths

from dataclasses import dataclass
from pathlib import Path
import subprocess
import tkinter as tk

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

    def validateExecutable(
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

    ffmpegResult: ValidateBinaryResult = validateExecutable(
        path=Paths.ffmpeg(),
        arguements=["-version"],
        expectedReturnCode=0
    )

    ffprobeResult: ValidateBinaryResult = validateExecutable(
        path=Paths.ffprobe(),
        arguements=["-version"],
        expectedReturnCode=0
    )

    qjsResult: ValidateBinaryResult = validateExecutable(
        path=Paths.qjs(),
        arguements=["--eval", "console.log('QuickJS is working!')"],
        expectedReturnCode=0
    )

    return ValidateBinariesResult(
        ffmpeg=ffmpegResult,
        ffprobe=ffprobeResult,
        qjs=qjsResult
    )

def setWidgetState(
    widget: tk.Widget,
    enabled: bool
) -> None:

    state: str = "normal" if enabled else "disabled"

    try:
        widget.configure(state=state)
    except tk.TclError:
        pass

    for childWidget in widget.winfo_children():
        setWidgetState(
            widget=childWidget,
            enabled=enabled
        )
