
from InfoDict import InfoDict

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar
import itertools

class MediaContainer(Enum):
    MP4 = "mp4"
    MKV = "mkv"
    WEBM = "webm"

mediaContainers: tuple[MediaContainer, ...] = tuple(MediaContainer)

@dataclass
class VideoData:

    type VideoHeight = int
    class VideoCodec(Enum):
        AV1 = "av01"
        VP8 = "vp8"
        AVC1 = "avc1"
        AVC3 = "avc3"
        MPEG4 = "mp4v"

    DEFAULT_MAXIMUM_VIDEO_HEIGHT: VideoHeight = 1080
    maximumVideoHeight: VideoHeight = DEFAULT_MAXIMUM_VIDEO_HEIGHT

    DEFAULT_VIDEO_CODEC: VideoCodec = VideoCodec.AV1
    videoCodec: VideoCodec = DEFAULT_VIDEO_CODEC
    videoCodecs: ClassVar[tuple[VideoCodec, ...]] = tuple(VideoCodec)

@dataclass
class AudioData:

    type AudioBitRate = int
    class AudioCodec(Enum):
        OPUS = "opus"
        MP4A = "mp4a"

    DEFAULT_MAXIMUM_AUDIO_BIT_RATE: AudioBitRate = 190
    maximumAudioBitRate: AudioBitRate = DEFAULT_MAXIMUM_AUDIO_BIT_RATE

    DEFAULT_AUDIO_CODEC: AudioCodec = AudioCodec.OPUS
    audioCodec: AudioCodec = DEFAULT_AUDIO_CODEC
    audioCodecs: ClassVar[tuple[AudioCodec, ...]] = tuple(AudioCodec)

@dataclass
class DownloadData:

    _id_counter: ClassVar[itertools.count] = itertools.count(start=1)

    type Id = int
    type Url = str | None
    type IsVideoDownload = bool
    type IsAudioDownload = bool
    type IsSubtitleDownload = bool
    type Title = str | None
    type ThumbnailLink = str | None
    type DownloadedBytes = float | None
    type TotalBytes = int | None
    type Progress = float

    id: Id = field(default_factory=lambda: next(DownloadData._id_counter))
    url: Url = None
    isVideoDownload: IsVideoDownload = True
    isAudioDownload: IsAudioDownload = True
    isSubtitleDownload: IsSubtitleDownload = False
    title: Title = None
    thumbnailLink: ThumbnailLink = None
    downloadedBytes: DownloadedBytes = None
    totalBytes: TotalBytes = None
    progress: Progress = 0.0
    mediaContainer: MediaContainer = MediaContainer.MP4
    videoData: VideoData = field(
        default_factory=lambda: VideoData(
            videoCodec=VideoData.VideoCodec.H264,
        )
    )
    audioData: AudioData = field(
        default_factory=lambda: AudioData(
            audioCodec=AudioData.AudioCodec.MP4A,
            maximumAudioBitRate=200
        )
    )

type DownloadDatas = dict[
    DownloadData.Id,
    DownloadData
]
