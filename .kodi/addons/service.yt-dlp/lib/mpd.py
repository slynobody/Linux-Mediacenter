# -*- coding: utf-8 -*-


from iapc import Client
from nuttig import getSetting, localizedString


# codecs -----------------------------------------------------------------------

__none_codec__ = "none"

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


def __include__(contentType, codec, ocodec, exclude):
    if (
        codec and
        (codec != __none_codec__) and
        (ocodec == __none_codec__) and
        (not codec.startswith(exclude))
    ):
        return contentType
        #return (contentType, codec)

def __filter__(vcodec, acodec, exclude):
    return (
        __include__("video", vcodec, acodec, exclude) or
        __include__("audio", acodec, vcodec, exclude)
    )

def __dash__(formats, exclude):
    return (
        fmt for fmt in formats
        if (
            fmt.get("container", "").endswith("_dash") and
            fmt.setdefault(
                "__contentType__",
                __filter__(fmt.get("vcodec"), fmt.get("acodec"), exclude)
            )
            #fmt.setdefault(
            #    "__stream_args__",
            #    __filter__(fmt.get("vcodec"), fmt.get("acodec"), exclude)
            #)
        )
    )


# ------------------------------------------------------------------------------
# YtDlpMpd

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


class YtDlpMpd(object):

    __service_id__ = "service.manifests.mpd"

    __fps_limits__ = {0: 32101, 30: 32102}

    __fps_hints__ = {
        "int":   {"label": 32201, "values": __IntFramerate__()},
        "float": {"label": 32202, "values": __FloatFramerate__()},
        "none":  {"label": 32203, "values": __NoFramerate__()}
    }

    __heights__ = {
        2160: {"label": 34101, "width": 3840},
        1440: {"label": 34102, "width": 2560},
        1080: {"label": 34103, "width": 1920},
        720:  {"label": 34104, "width": 1280},
        480:  {"label": 34105, "width": 854},
        360:  {"label": 34106, "width": 640},
        0:    {"label": 90011, "width": 0}
    }

    # --------------------------------------------------------------------------

    def __init__(self, logger):
        self.logger = logger.getLogger(component="mpd")
        self.__manifests__ = Client(self.__service_id__)
        self.__streamTypes__ = {
            "video": self.__video_stream__, "audio": self.__audio_stream__
        }
        self.__supportedSubtitles__ = ("vtt",)

    def __setup__(self):
        # fps limit
        self.__fps_limit__ = getSetting("fps.limit", int)
        self.logger.info(
            f"{localizedString(32100)}: "
            f"{localizedString(self.__fps_limits__[self.__fps_limit__])}"
        )
        # fps hint
        self.__fps_hint__ = getSetting("fps.hint", str)
        self.logger.info(
            f"{localizedString(32200)}: "
            f"{localizedString(self.__fps_hints__[self.__fps_hint__]['label'])}"
        )
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
        # preferred resolution
        self.__height__ = getSetting("prefs.height", int)
        self.logger.info(
            f"{localizedString(34100)}: "
            f"{localizedString(self.__heights__[self.__height__]['label'])}"
        )

    def __stop__(self):
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def __video_stream__(
        self, fmt, fps_limit=0, fps_hint="int", height=None, **kwargs
    ):
        fps = fmt["fps"]
        if ((not fps_limit) or (fps <= fps_limit)):
            stream = {
                "codecs": fmt["vcodec"],
                "bandwidth": int(fmt["vbr"] * 1000),
                "width": fmt["width"],
                "height": fmt["height"],
                "frameRate": self.__fps_hints__[fps_hint]["values"][fps]
            }
            if (
                height and
                (
                    (fmt.get("height", 0) == height) or
                    (
                        (height := self.__heights__.get(height, {})) and
                        fmt.get("width", 0) == height["width"]
                    )
                )

            ):
                stream["default"] = True
            return stream

    def __audio_stream__(self, fmt, inputstream="adaptive", **kwargs):
        stream = {
            "codecs": fmt["acodec"],
            "bandwidth": int(fmt["abr"] * 1000),
            "lang": fmt["language"],
            "audioSamplingRate": fmt["asr"],
            "audioChannels": fmt.get("audio_channels", 2)
        }
        if inputstream == "adaptive": # isa custom attributes
            stream.update(
                original=fmt.get("audioIsOriginal", False),
                default=fmt.get("audioIsDefault", False),
                impaired=fmt.get("audioIsDescriptive", False)
            )
        return stream

    # --------------------------------------------------------------------------

    def __streams__(self, formats, exclude=None, **kwargs):
        for fmt in __dash__(formats, exclude or tuple()):
            contentType = fmt["__contentType__"]
            if (stream := self.__streamTypes__[contentType](fmt, **kwargs)):
                yield dict(
                    stream,
                    contentType=contentType,
                    mimeType=f"{contentType}/{fmt['ext']}",
                    id=fmt["format_id"],
                    url=fmt["url"],
                    indexRange=fmt.get("indexRange", {}),
                    initRange=fmt.get("initRange", {})
                )

    def __subtitles__(self, subtitles):
        for lang, subs in subtitles.items():
            for sub in subs:
                if (
                    (id := sub.get("name")) and
                    ((ext := sub["ext"]) in self.__supportedSubtitles__)
                ):
                    yield dict(
                        contentType="text",
                        mimeType=f"text/{ext}",
                        lang=lang,
                        id=id,
                        url=sub["url"]
                    )

    def __manifest__(self, duration, formats, subtitles, **kwargs):
        if (streams := list(self.__streams__(formats, **kwargs))):
            streams.extend(self.__subtitles__(subtitles))
            return self.__manifests__.manifest(duration, streams)

    # manifest -----------------------------------------------------------------

    def manifest(
        self,
        *args,
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
        return self.__manifest__(
            *args,
            exclude=__excludes__(exclude) if exclude else None,
            fps_limit=fps_limit,
            fps_hint=fps_hint,
            height=height,
            inputstream=inputstream,
            **kwargs
        )
