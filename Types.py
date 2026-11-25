
from InfoDict import InfoDict

from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar
import itertools

class MediaContainerFormat(Enum):
    MP4 = "mp4"
    MKV = "mkv"
    WEBM = "webm"

DEFAULT_MEDIA_CONTAINER_FORMAT = MediaContainerFormat.WEBM

MEDIA_CONTAINER_FORMATS: tuple[MediaContainerFormat, ...] = tuple(MediaContainerFormat)
MEDIA_CONTAINER_FORMATS_STR: tuple[str, ...] = tuple(mediaContainerFormat.value for mediaContainerFormat in MediaContainerFormat)

@dataclass
class VideoData:

    type VideoHeight = int
    class VideoCodec(Enum):
        AV1 = "av01"
        VP8 = "vp8"
        AVC1 = "avc1"
        AVC3 = "avc3"
        MPEG4 = "mp4v"

    DEFAULT_MAXIMUM_VIDEO_HEIGHT: VideoHeight = 720
    maximumVideoHeight: VideoHeight = DEFAULT_MAXIMUM_VIDEO_HEIGHT

    DEFAULT_VIDEO_CODEC: VideoCodec = VideoCodec.AV1
    videoCodec: VideoCodec = DEFAULT_VIDEO_CODEC
    VIDEO_CODECS: ClassVar[tuple[VideoCodec, ...]] = tuple(VideoCodec)
    VIDEO_CODECS_STR: ClassVar[tuple[str, ...]] = tuple(videoCodec.value for videoCodec in VideoCodec)

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
    AUDIO_CODECS: ClassVar[tuple[AudioCodec, ...]] = tuple(AudioCodec)
    AUDIO_CODECS_STR: ClassVar[tuple[str, ...]] = tuple(audioCodec.value for audioCodec in AudioCodec)

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
    mediaContainerFormat: MediaContainerFormat = DEFAULT_MEDIA_CONTAINER_FORMAT
    videoData: VideoData = field(default_factory=VideoData)
    audioData: AudioData = field(default_factory=AudioData)

type DownloadDatas = dict[
    DownloadData.Id,
    DownloadData
]
