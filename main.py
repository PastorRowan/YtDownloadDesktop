
from dataclasses import dataclass, field

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont

import threading
import yt_dlp_package_manager

from collections import deque

import itertools
import time

from enum import Enum

import InfoDict

import os

from typing import ClassVar

from Paths import Paths

def validate_tools():
    for tool in [
        Paths.ffmpeg(),
        Paths.ffprobe(),
        Paths.qjs()
    ]:
        print(f"Looking for executable at '{tool}'")
        if not os.path.isfile(tool) or not os.access(tool, os.X_OK):
            raise FileNotFoundError(
                f"Missing or not executable: {tool}"
            )

@dataclass
class VideoData:

    class VideoCodec(Enum):
        AV1 = "av1"
        VP8 = "vp8"
        H264 = "h264"
        H265 = "h265"
        MPEG4 = "mpeg4"
    type VideoHeight = int | None

    videoCodec: VideoCodec
    maximumVideoHeight: VideoHeight

@dataclass
class AudioData:

    class AudioCodec(Enum):
        OPUS = "opus"
        MP4A = "mp4a"
    type AudioBitRate = int | None

    audioCodec: AudioCodec
    maximumAudioBitRate: AudioBitRate

class MediaContainer(Enum):
    MP4 = "mp4"
    MKV = "mkv"
    WEBM = "webm"

@dataclass
class DownloadData:

    _id_counter: ClassVar[itertools.count] = itertools.count(start=1)

    type Id = int
    type Url = str | None
    class DownloadType(Enum):
        VIDEO = "video"
        AUDIO = "audio"
    type Title = str | None
    type ThumbnailLink = str | None
    type DownloadedBytes = float | None
    type TotalBytes = int | None
    type Progress = float | None

    id: Id = field(default_factory=lambda: next(DownloadData._id_counter))
    url: Url = None
    downloadType: DownloadType = DownloadType.VIDEO
    title: Title = None
    thumbnailLink: ThumbnailLink = None
    downloadedBytes: DownloadedBytes = None
    totalBytes: TotalBytes = None
    progress: Progress = None
    videoData: VideoData = field(
        default_factory=lambda: VideoData(
            videoCodec=VideoData.VideoCodec.H264,
            maximumVideoHeight=1080
        )
    )
    audioData: AudioData = field(
        default_factory=lambda: AudioData(
            audioCodec=AudioData.AudioCodec.MP4A,
            maximumAudioBitRate=200
        )
    )
    mediaContainer: MediaContainer = MediaContainer.MP4

class DownloadQueue:

    def __init__(self) -> None:
        self._deque: deque[DownloadData] = deque()
        self._dequeRLock: threading.RLock = threading.RLock()
        self._condition = threading.Condition(self._dequeRLock)
        self._worker: threading.Thread = threading.Thread(
            target=self._download,
            daemon=True
        )
        self._worker.start()

    """
    WARNING: method does not acquire dequeue lock, locking must be done by the calling function
    """
    def _getDownloadDataById(
        self,
        downloadId: DownloadData.Id
    ) -> DownloadData | None:
        downloadData: DownloadData | None = None
        for currentDownloadData in self._deque:
            if currentDownloadData.id == downloadId:
                downloadData = currentDownloadData
                break
        return downloadData

    def _download(self) -> None:
        UPDATE_INTERVAL: float = 1.5
        while True:

            with self._condition:
                while not self._deque:
                    self._condition.wait()

            try:

                downloadData: DownloadData | None = None
                downloadDataId: DownloadData.Id | None = None

                with self._dequeRLock:
                    downloadData = self._deque[0]
                    downloadDataId = downloadData.id

                if downloadData is None or downloadDataId is None:
                    print(f"Error: failed to get the 1st download")
                    continue

                if downloadData.url == None:
                    print(f"Error: download with id '{downloadData.id}' has no url, removing download from DownloadQueue")
                    self.removeDownloadById(downloadData.id)
                    continue

                last_update_time: float = 0.0
                def progressHook(data):
                    nonlocal downloadDataId
                    nonlocal last_update_time

                    now: float = time.time()

                    # throttle downloadData updates
                    if now - last_update_time < UPDATE_INTERVAL:
                        return

                    last_update_time = now

                    downloadedBytes: DownloadData.DownloadedBytes = data.get("downloaded_bytes")
                    totalBytes: DownloadData.TotalBytes = data.get("total_bytes") or data.get("total_bytes_estimate")

                    progress: DownloadData.Progress = None
                    if downloadedBytes is not None and totalBytes is not None:
                        progress = downloadedBytes / totalBytes

                    if self._dequeRLock.acquire(blocking=False):
                        try:
                            downloadData: DownloadData | None = self._getDownloadDataById(downloadDataId)
                            if downloadData is None:
                                return
                            downloadData.downloadedBytes = downloadedBytes
                            downloadData.totalBytes = totalBytes
                            downloadData.progress = progress
                        except Exception as e:
                            print(f"Error: failed to update download data with id '{downloadDataId}' for download with ")
                        finally:
                            self._dequeRLock.release()

                baseOptions = {
                    "ffmpeg_location": str(Paths.ffmpeg()),
                    "js_runtimes": {
                        "quickjs": {
                            "path": str(Paths.qjs())
                        }
                    },
                    "remote_components": ["ejs:github"],
                    "progress_hooks": [progressHook],
                    "cachedir": str(Paths.yt_dlp_cache_dir()),
                    "no_color": True,
                    "retries": 10,
                    "fragment_retries": 10,
                    "concurrent_fragments": 16,
                    "merge_output_format": downloadData.mediaContainer.value,
                    "postprocessor_args": {
                        "ffmpeg": [
                            "-threads",
                            str(os.cpu_count() or 1)
                        ]
                    }
                }

                videoOptions = {
                    **baseOptions,
                    "format": (
                        f"bv*[height<={downloadData.videoData.maximumVideoHeight}]+"
                        f"ba*[abr<={downloadData.audioData.maximumAudioBitRate}]"
                        f"/b[height<={downloadData.videoData.maximumVideoHeight}]"
                    )
                }

                audioOptions = {
                    **baseOptions,
                    "format": (
                        f"ba*[abr<={downloadData.audioData.maximumAudioBitRate}]/ba"
                    ),
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": downloadData.audioData.audioCodec
                    }]
                }

                downloadOptions = None
                if downloadData.downloadType == DownloadData.DownloadType.VIDEO:
                    downloadOptions = videoOptions
                elif downloadData.downloadType == DownloadData.DownloadType.AUDIO:
                    downloadOptions = audioOptions
                else:
                    raise ValueError(f"Error: download data with id '{downloadDataId}' has invalid or unsupported download type '{downloadData.downloadType}'")

                import yt_dlp

                with yt_dlp.YoutubeDL(downloadOptions) as ydl_download: 

                    infoDict = ydl_download.extract_info(
                        url=downloadData.url,
                        download=True
                    )

            except Exception as e:
                print("Failed to download media: ", e)
            finally:
                self.removeDownloadById(downloadData.id)

    def getDownloads(self) -> list[DownloadData]:
        with self._dequeRLock:
            return list(self._deque)

    def addDownload(
        self,
        downloadData: DownloadData
    ) -> bool:
        try:
            with self._dequeRLock:
                self._deque.append(downloadData)
                self._condition.notify()
                return True
        except Exception as e:
            print("Failed to add download to DownloadQueue: ", e)
            return False

    def removeDownloadById(
        self,
        downloadId: DownloadData.Id
    ) -> bool:
        try:
            with self._dequeRLock:

                downloadData: DownloadData | None = self._getDownloadDataById(downloadId)

                if downloadData is not None:
                    self._deque.remove(downloadData)
                    return True

                return False

        except Exception as e:
            print("Failed to remove download from DownloadQueue: ", e)
            return False

def main():

    downloadQueue: DownloadQueue = DownloadQueue()

    def on_video_link_entry_key_press(event: tk.Event):
        print("Current value:", event.widget.get())
        videoUrl: str = event.widget.get()
        downloadQueue.addDownload(
            DownloadData(
                url=videoUrl
            )
        )

    root: tk.Tk = tk.Tk()
    root.title("YtDownloadDesktop")
    root.minsize(
        width=640,
        height=480
    )

    default_font: tkFont.Font = tkFont.nametofont("TkDefaultFont")
    default_font.configure(
        family="Segoe UI",
        size=10
    )

    text_font: tkFont.Font = tkFont.nametofont("TkTextFont")
    text_font.configure(
        family="Segoe UI",
        size=10
    )

    updatingYtDlpPlaceholderLabel: ttk.Label = ttk.Label(
        master=root,
        text="Updating yt-dlp..."
    )
    updatingYtDlpPlaceholderLabel.pack()

    def on_yt_dlp_update_finish():

        updatingYtDlpPlaceholderLabel.pack_forget()

        titleLabel: ttk.Label = ttk.Label(
            master=root,
            text="YtDownloadDesktop"
        )
        titleLabel.pack()

        # Spacer
        ttk.Frame(
            master=root,
            width=1,
            height=20
        ).pack()

        videoLinkEntryLabel: ttk.Label = ttk.Label(
            master=root,
            text="Video link"
        )
        videoLinkEntryLabel.pack()

        videoLinkEntry: ttk.Entry = ttk.Entry(
            master=root
        )
        videoLinkEntry.bind(
            "<Return>",
            on_video_link_entry_key_press
        )
        videoLinkEntry.pack()

        downloadFrame: ttk.Frame = ttk.Frame(
            master=root
        )
        downloadFrame.pack()
        downloadThumbnailLabel: ttk.Label = ttk.Label(
            master=downloadFrame
        )
        downloadThumbnailLabel.pack()
        downloadProgressBar: ttk.Progressbar = ttk.Progressbar(
            master=downloadFrame,
            orient="horizontal",
            mode="determinate",
            maximum=100,
            value=0
        )
        downloadProgressBar.pack(fill="x")

    def update_yt_dlp_worker():
        try:
            yt_dlp_package_manager.update_yt_dlp()
        except Exception as e:
            print("Failed to update yt-dlp:", e)
        finally:
            root.after(0, on_yt_dlp_update_finish)

    t = threading.Thread(
        target=update_yt_dlp_worker
    )
    t.start()

    root.mainloop()

if __name__ == "__main__":
    main()

"""
        testThumbnail: tk.PhotoImage = tk.PhotoImage(file="test.png")
        downloadThumbnailLabel.image = testThumbnail
"""
