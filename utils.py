
from Paths import Paths

from dataclasses import dataclass
import os
import subprocess

@dataclass
class ValidateBinaryResult:
    isInstalled: bool
    isWorking: bool

@dataclass
class ValidateBinariesResult:

    ffmpeg: ValidateBinaryResult
    ffprobe: ValidateBinaryResult
    qjs: ValidateBinaryResult

    @property
    def isWorking(self) -> bool:
        return (
            self.ffmpeg.isWorking
            and self.ffprobe.isWorking
            and self.qjs.isWorking
        )

def validateBinaries() -> ValidateBinariesResult:

    def validateExecutable(tool: str) -> ValidateBinaryResult:

        print(f"\nLooking for executable at '{tool}'...")

        isInstalled: bool = os.path.isfile(tool)

        if not isInstalled:
            print(f"Missing executable: '{tool}'")
            return ValidateBinaryResult(
                isInstalled=False,
                isWorking=False
            )

        print(f"Found executable: '{tool}'")

        try:
            result = subprocess.run(
                [tool, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            isWorking: bool = result.returncode == 0

            if isWorking:
                versionOutput = (
                    result.stdout.strip()
                    or result.stderr.strip()
                )
                print(f"Executable working:\n{versionOutput}")
            else:
                print(
                    f"Executable failed with exit code "
                    f"{result.returncode}:\n{result.stderr.strip()}"
                )

            return ValidateBinaryResult(
                isInstalled=isInstalled,
                isWorking=isWorking
            )

        except subprocess.TimeoutExpired:
            print(f"Executable timed out: '{tool}'")

        except OSError as e:
            print(f"Failed to execute '{tool}': {e}")

        return ValidateBinaryResult(
            isInstalled=True,
            isWorking=False
        )

    ffmpegResult: ValidateBinaryResult = validateExecutable(
        str(Paths.ffmpeg())
    )

    ffprobeResult: ValidateBinaryResult = validateExecutable(
        str(Paths.ffprobe())
    )

    qjsResult: ValidateBinaryResult = validateExecutable(
        str(Paths.qjs())
    )

    return ValidateBinariesResult(
        ffmpeg=ffmpegResult,
        ffprobe=ffprobeResult,
        qjs=qjsResult
    )
