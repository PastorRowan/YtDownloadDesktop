
import Types
from Paths import Paths

import threading
import time
import os
import copy

class DownloadQueue:

    def __init__(self) -> None:
        self._downloadDatas: Types.DownloadDatas = {}
        self._downloadDatasRLock: threading.RLock = threading.RLock()
        self._condition = threading.Condition(self._downloadDatasRLock)
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
        downloadId: Types.DownloadData.Id
    ) -> Types.DownloadData | None:
        return self._downloadDatas.get(downloadId)

    def _download(self) -> None:
        UPDATE_INTERVAL: float = 1.5
        while True:

            with self._condition:
                while not self._downloadDatas:
                    self._condition.wait()

            try:

                downloadData: Types.DownloadData | None = None
                downloadDataId: Types.DownloadData.Id = -1

                with self._downloadDatasRLock:
                    downloadData = next(iter(self._downloadDatas.values()), None)
                    if downloadData is not None:
                        downloadDataId = downloadData.id
                    else:
                        raise Exception("downloadData is None because queue is empty")

                if (
                    downloadData is None
                ) or (
                    downloadDataId is None
                ) or (
                    (
                        not downloadData.isVideoDownload and
                        not downloadData.isAudioDownload and
                        not downloadData.isSubtitleDownload
                    )
                ):
                    print(f"Error: failed to get the 1st download or no download media was selected")
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

                    downloadedBytes: Types.DownloadData.DownloadedBytes = data.get("downloaded_bytes")
                    totalBytes: Types.DownloadData.TotalBytes = data.get("total_bytes") or data.get("total_bytes_estimate")

                    progress: Types.DownloadData.Progress = 0
                    if downloadedBytes is not None and totalBytes is not None:
                        progress = downloadedBytes / totalBytes

                    infoDict: Types.InfoDict = data.get("info_dict", {})

                    title: Types.DownloadData.Title = infoDict.get("title")

                    if self._downloadDatasRLock.acquire(blocking=False):
                        try:
                            downloadData: Types.DownloadData | None = self._getDownloadDataById(downloadDataId)
                            if downloadData is None:
                                return
                            if downloadedBytes is not None:
                                downloadData.downloadedBytes = downloadedBytes
                            if totalBytes is not None:
                                downloadData.totalBytes = totalBytes
                            downloadData.progress = progress
                            if title is not None:
                                downloadData.title = title
                        except Exception as e:
                            print(f"Error: failed to update download data with id '{downloadDataId}' for download with ")
                        finally:
                            self._downloadDatasRLock.release()

                downloadOptions = {
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

                    "skip_download": (
                        not downloadData.isVideoDownload and
                        not downloadData.isAudioDownload
                    ),
                    "writesubtitles": downloadData.isSubtitleDownload,
                    "writeautomaticsub": downloadData.isSubtitleDownload,
                    "subtitleslangs": (
                        ["all"] if downloadData.isSubtitleDownload else None
                    ),
                    "subtitlesformat": (
                        "best" if downloadData.isSubtitleDownload else None
                    ),

                    "merge_output_format": (
                        downloadData.mediaContainer.value if downloadData.isVideoDownload and downloadData.isAudioDownload else None
                    ),
                    "remuxvideo": (
                        downloadData.mediaContainer.value
                        if downloadData.isVideoDownload
                        else None
                    ),
                    "postprocessor_args": {
                        "ffmpeg": [
                            "-threads",
                            str(os.cpu_count() or 1)
                        ]
                    },

                }

                """
                maybe need it
                    "postprocessors": (
                        [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": downloadData.audioData.audioCodec
                        }]
                        if downloadData.isAudioDownload and not downloadData.isVideoDownload
                        else None
                    )
                """

                videoFormat: str = (
                    f"bv*"
                    f"[height<={downloadData.videoData.maximumVideoHeight}]"
                    f"[vcodec^={downloadData.videoData.videoCodec.value}]"
                )

                audioFormat: str = (
                    f"ba*"
                    f"[abr<={downloadData.audioData.maximumAudioBitRate}]"
                    f"[acodec^={downloadData.audioData.audioCodec.value}]"
                )

                formatString: str | None = (
                    f"{videoFormat}+{audioFormat}"
                    if downloadData.isVideoDownload and downloadData.isAudioDownload
                    else videoFormat
                    if downloadData.isVideoDownload
                    else audioFormat
                    if downloadData.isAudioDownload
                    else None
                )

                downloadOptions["format"] = formatString

                # Remove options that are not applicable.
                downloadOptions = {
                    key: value
                    for key, value in downloadOptions.items()
                    if value is not None
                }

                import yt_dlp

                with yt_dlp.YoutubeDL(downloadOptions) as ydl_download: 

                    infoDict = ydl_download.extract_info(
                        url=downloadData.url,
                        download=True
                    )

            except Exception as e:
                print("Failed to download media: ", e)
            finally:
                if downloadData is not None:
                    self.removeDownloadById(downloadData.id)

    def getDownloads(self) -> Types.DownloadDatas:
        with self._downloadDatasRLock:
            return copy.deepcopy(self._downloadDatas)

    def addDownload(
        self,
        downloadData: Types.DownloadData
    ) -> bool:
        try:
            with self._downloadDatasRLock:
                if downloadData.id in self._downloadDatas:
                    return False
                self._downloadDatas[downloadData.id] = downloadData
                self._condition.notify()
                return True
        except Exception as e:
            print("Failed to add download to DownloadQueue: ", e)
            return False

    def removeDownloadById(
        self,
        downloadId: Types.DownloadData.Id
    ) -> bool:
        try:
            with self._downloadDatasRLock:

                downloadData: Types.DownloadData | None = self._getDownloadDataById(downloadId)

                if downloadData is not None:
                    return self._downloadDatas.pop(
                        downloadId,
                        None
                    ) is not None

                return False

        except Exception as e:
            print("Failed to remove download from DownloadQueue: ", e)
            return False
