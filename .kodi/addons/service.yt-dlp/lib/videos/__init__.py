# -*- coding: utf-8 -*-


from importlib import import_module

from iapc import Client
from nuttig import getSetting, localizedString

from videos import languages


# ------------------------------------------------------------------------------
# YtDlpVideo

class YtDlpVideo(dict):

    def __init__(self, info):
        if (url := info.get("manifest_url", "")):
            manifestType, mimeType = ("hls", "application/x-mpegURL")
        else:
            manifestType, mimeType = ("mpd", "application/dash+xml")
        super(YtDlpVideo, self).__init__(
            extractor=info["extractor"],
            video_id=info.get("id"),
            title=info.get("fulltitle", ""),
            description=info.get("description", ""),
            channel_id=info.get("channel_id"),
            channel=info.get("channel", ""),
            duration=info.get("duration", -1),
            is_live=info.get("is_live", False),
            thumbnail=info.get("thumbnail"),
            like_count=info.get("like_count", 0),
            view_count=info.get("view_count", 0),
            timestamp=info.get("timestamp", 0),
            headers=info.get("http_headers", {}),
            language=info.get("language", ""),
            url=url,
            manifestType=manifestType,
            mimeType=mimeType
        )


# codecs -----------------------------------------------------------------------

NoneCodec = "none"

__codecs__ = {
    "avc1": {"contentType": "video", "label": 33101, "names": ("avc1", )},
    "mp4a": {"contentType": "audio", "label": 33102, "names": ("mp4a", )},
    "vp09": {"contentType": "video", "label": 33103, "names": ("vp09", "vp9")},
    "opus": {"contentType": "audio", "label": 33104, "names": ("opus", )},
    "av01": {
        "contentType": "video",
        "label": 33105,
        "names": ("av01", ),
        "experimental": True
    }
}


def __contentType_codecs__(contentType):
    return set(
        key for key, codec in __codecs__.items()
        if (
            (codec["contentType"] == contentType) and
            (not codec.get("experimental", False))
        )
    )


__video_codecs__ = __contentType_codecs__("video")
__audio_codecs__ = __contentType_codecs__("audio")


def __excludes__(exclude):
    exclude = set(exclude)
    if __video_codecs__ <= exclude:
        exclude.remove("avc1") # fallback to h264
    if __audio_codecs__ <= exclude:
        exclude.remove("mp4a") # fallback to aac
    return tuple(
        name for names in (
            __codecs__[codec]["names"]
            for codec in exclude
            if codec in __codecs__
        ) for name in names
    )


# subs -------------------------------------------------------------------------

__supportedSubtitles__ = ("vtt",)


def __subtitles__(subtitles):
    for language, _subtitles_ in subtitles.items():
        if (name := languages.language_name(language)):
            for subtitle in _subtitles_:
                if ((ext := subtitle["ext"]) in __supportedSubtitles__):
                    yield dict(
                        language=language,
                        name=name,
                        uri=subtitle["url"],
                        ext=ext,
                        protocol=subtitle.get("protocol")
                    )


# ------------------------------------------------------------------------------

FpsLimits = {0: 32101, 30: 32102}


class __IntFramerate__(dict):

    def __missing__(self, key):
        return key


class __FloatFramerate__(__IntFramerate__):

    def __init__(self):
        super(__FloatFramerate__, self).__init__(
            {24: 23.976, 30: 29.97, 60: 59.94}
        )


class __NoFramerate__(dict):

    def __missing__(self, key):
        return 0


FpsHints = {
    "int":   {"label": 32201, "values": __IntFramerate__()},
    "float": {"label": 32202, "values": __FloatFramerate__()},
    "none":  {"label": 32203, "values": __NoFramerate__()}
}


VideoHeights = {
    2160: {"label": 34101, "width": 3840},
    1440: {"label": 34102, "width": 2560},
    1080: {"label": 34103, "width": 1920},
    720:  {"label": 34104, "width": 1280},
    480:  {"label": 34105, "width": 854},
    360:  {"label": 34106, "width": 640},
    0:    {"label": 90011, "width": 0}
}

def defaultResolution(fmt, height):
    if (
        (fmt.get("height", 0) == height) or
        (
            (height := VideoHeights.get(height, {})) and
            (fmt.get("width", 0) == height["width"])
        )
    ):
        return True
    return False


# ------------------------------------------------------------------------------
# YtDlpVideos

class YtDlpVideos(object):

    __manifests_id__ = "service.manifests"

    # --------------------------------------------------------------------------

    def __init__(self, logger):
        self.logger = logger.getLogger(component="videos")
        self.__manifests__ = Client(self.__manifests_id__)

    def __setup__(self):
        # include automatic captions
        self.__captions__ = getSetting("subs.captions", bool)
        self.logger.info(f"{localizedString(31100)}: {self.__captions__}")
        # exclude codecs
        self.__exclude__ = []
        labels = None
        if (exclude := getSetting("codecs.exclude")):
            self.__exclude__ = exclude.split(",")
            labels = ", ".join(
                localizedString(__codecs__[codec]["label"])
                for codec in self.__exclude__
            )
        self.logger.info(f"{localizedString(33100)}: {labels}")
        # fps limit
        self.__fps_limit__ = getSetting("fps.limit", int)
        self.logger.info(
            f"{localizedString(32100)}: "
            f"{localizedString(FpsLimits[self.__fps_limit__])}"
        )
        # fps hint
        self.__fps_hint__ = getSetting("fps.hint", str)
        self.logger.info(
            f"{localizedString(32200)}: "
            f"{localizedString(FpsHints[self.__fps_hint__]['label'])}"
        )
        # preferred resolution
        self.__height__ = getSetting("prefs.height", int)
        self.logger.info(
            f"{localizedString(34100)}: "
            f"{localizedString(VideoHeights[self.__height__]['label'])}"
        )

    def __stop__(self):
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def manifest(
        self,
        video,
        formats,
        subtitles,
        exclude=None,
        fps_limit=None,
        fps_hint=None,
        height=None,
        inputstream=None,
        **kwargs
    ):
        exclude = exclude if exclude is not None else self.__exclude__
        fps_limit = fps_limit if fps_limit is not None else self.__fps_limit__
        fps_hint = fps_hint if fps_hint is not None else self.__fps_hint__
        height = height or self.__height__
        inputstream = inputstream if inputstream is not None else "adaptive"
        self.logger.info(
            f"manifest("
                f"exclude={exclude}, "
                f"fps_limit={fps_limit}, "
                f"fps_hint={fps_hint}, "
                f"height={height}, "
                f"inputstream={inputstream}, "
                f"kwargs={kwargs}"
            f")"
        )
        return self.__manifests__.manifest(
            (_type_ := video["manifestType"]),
            *import_module(f"videos.{_type_}").streams(
                video,
                formats,
                subtitles,
                exclude=__excludes__(exclude) if exclude else None,
                fps_limit=fps_limit,
                fps_hint=fps_hint,
                height=height,
                inputstream=inputstream,
                **kwargs
            )
        )

    # video --------------------------------------------------------------------

    def video(self, info, captions=None, **kwargs):
        if (
            (not (subtitles := info.get("subtitles", {}))) and
            (bool(captions) if (captions is not None) else self.__captions__)
        ):
            subtitles = info.get("automatic_captions", {})
        formats = info.get("formats", [])
        #self.logger.info(f"formats = {formats}")
        video = YtDlpVideo(info)
        if (
            (not video["url"]) or
            ((video["extractor"] == "youtube") and (not video["is_live"]))
        ):
            video["url"] = self.manifest(
                video, formats, __subtitles__(subtitles), **kwargs
            )
        return video
