
from InfoDict import InfoDict

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar
import itertools

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
    type Progress = float

    id: Id = field(default_factory=lambda: next(DownloadData._id_counter))
    url: Url = None
    downloadType: DownloadType = DownloadType.VIDEO
    title: Title = None
    thumbnailLink: ThumbnailLink = None
    downloadedBytes: DownloadedBytes = None
    totalBytes: TotalBytes = None
    progress: Progress = 0.0
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

type DownloadDatas = dict[
    DownloadData.Id,
    DownloadData
]
